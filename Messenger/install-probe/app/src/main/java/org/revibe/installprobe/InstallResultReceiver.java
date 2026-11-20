package org.revibe.installprobe;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInstaller;
import android.os.Build;
/** Private status receiver for user-approved package sessions; no raw logs. */
public final class InstallResultReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        if (intent == null || Build.VERSION.SDK_INT < 21) return;
        int status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE);
        if (status == PackageInstaller.STATUS_PENDING_USER_ACTION) {
            Intent approval = intent.getParcelableExtra(Intent.EXTRA_INTENT);
            if (approval != null) {
                try {
                    approval.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    context.startActivity(approval);
                    InstallerState.setResult(context, "Android requested installation approval. Confirm or cancel there.");
                    return;
                } catch (RuntimeException ignored) {
                    InstallerState.setResult(context, "Android approval screen could not open. Installation is not confirmed.");
                    return;
                }
            }
            InstallerState.setResult(context, "Android approval is required but no confirmation screen was supplied.");
            return;
        }
        String label = InstallStatus.category(status);
        String code = InstallStatus.failureCode(
            intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE));
        if (!code.isEmpty()) label += " (" + code + ")";
        InstallerState.setResult(context, label);
    }
}
