package org.revibe.installprobe;

import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInstaller;
import android.content.pm.PackageManager;
import android.os.Bundle;

/**
 * On-emulator callback contract checks without installing a third-party APK.
 * These intentionally synthesize PackageInstaller results. This is not an
 * end-to-end file picker or package-install test.
 */
public final class InstallCallbackInstrumentation extends Instrumentation {
    private int checked = 0;

    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        start();
    }

    private void assertThat(boolean expected, String reason) {
        checked++;
        if (!expected) throw new AssertionError(reason);
    }

    private String simulate(Context context, int status, String details) {
        Intent callback = new Intent(context, InstallResultReceiver.class);
        callback.putExtra(PackageInstaller.EXTRA_STATUS, status);
        if (details != null) {
            callback.putExtra(PackageInstaller.EXTRA_STATUS_MESSAGE, details);
        }
        new InstallResultReceiver().onReceive(context, callback);
        return InstallerState.lastResult(context);
    }

    @Override public void onStart() {
        super.onStart();
        Bundle result = new Bundle();
        try {
            Context app = getTargetContext();
            app.getSharedPreferences("revibe_install_test", Context.MODE_PRIVATE).edit().clear().commit();

            String incompatible = simulate(app,
                PackageInstaller.STATUS_FAILURE_INCOMPATIBLE,
                "INSTALL_FAILED_NO_MATCHING_ABIS username=private_example");
            assertThat(incompatible.contains("APK not compatible"), "wrong incompatibility category");
            assertThat(incompatible.contains("INSTALL_FAILED_NO_MATCHING_ABIS"),
                "sanitized package manager code missing");
            assertThat(!incompatible.contains("private_example"), "raw error details leaked");

            String conflict = simulate(app, PackageInstaller.STATUS_FAILURE_CONFLICT,
                "INSTALL_FAILED_UPDATE_INCOMPATIBLE sensitive/path");
            assertThat(conflict.contains("Package or signing conflict"), "wrong conflict category");
            assertThat(!conflict.contains("sensitive/path"), "raw path leaked");

            String storage = simulate(app, PackageInstaller.STATUS_FAILURE_STORAGE, null);
            assertThat(storage.contains("Not enough installation storage"), "storage category missing");
            String blocked = simulate(app, PackageInstaller.STATUS_FAILURE_BLOCKED, null);
            assertThat(blocked.contains("blocked by device policy"), "blocked category missing");

            String missingApproval = simulate(app, PackageInstaller.STATUS_PENDING_USER_ACTION, null);
            assertThat(missingApproval.contains("no confirmation screen"), "missing approval wasn't reported");

            String success = simulate(app, PackageInstaller.STATUS_SUCCESS, "private-data-to-hide");
            assertThat(success.equals("Installed successfully"), "unexpected success detail");
            assertThat(!success.contains("private-data-to-hide"), "success path leaked details");

            assertThat(AllowedApks.matches("com.facebook.orca",
                "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab"),
                "audited original ARM64 APK rejected");
            assertThat(AllowedApks.matches("com.facebook.orca",
                "006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8"),
                "audited original ARM32 APK rejected");
            assertThat(AllowedApks.matches("org.revibe.orca01",
                "4eaf15fe989b62c51f86a5145d848f12fe63ccef581ee0d6c5ffd964b4a9b1ec"),
                "audited isolated APK rejected");
            assertThat(!AllowedApks.matches("com.facebook.orca",
                "0000000000000000000000000000000000000000000000000000000000000000"),
                "lookalike APK checksum accepted");
            assertThat(!AllowedApks.matches("com.example.malware",
                "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab"),
                "unexpected package name accepted");
            assertThat("abcd".equals(AllowedApks.hex(new byte[]{(byte)0xab, (byte)0xcd})),
                "SHA256 hex encoding corrupted");

            assertThat(app.getPackageManager().checkPermission(
                "android.permission.INTERNET", app.getPackageName())
                == PackageManager.PERMISSION_DENIED, "network permission present");

            result.putInt("assertions", checked);
            result.putString("result", "PASS - runtime callback privacy/category checks");
            result.putString(Instrumentation.REPORT_KEY_STREAMRESULT,
                "PASS: " + checked + " on-emulator assertions; no real APK install was attempted.");
            finish(0, result);
        } catch (Throwable error) {
            result.putString("result", "FAILED");
            // Report only assertion labels / exception type, never device identifiers.
            result.putString(Instrumentation.REPORT_KEY_STREAMRESULT,
                "FAILED: " + error.getClass().getSimpleName() + ": " + error.getMessage());
            finish(-1, result);
        }
    }
}
