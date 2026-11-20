package org.revibe.installprobe;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.security.MessageDigest;

/** A real independent Android diagnostic, NOT Messenger. No network access. */
public final class MainActivity extends Activity {
    private static final int CHOOSE_APK = 42;
    private static final long APK_LIMIT = 250L * 1024L * 1024L;
    private TextView status;
    private Button choose;

    private int dip(int dp) {
        return (int) (dp * getResources().getDisplayMetrics().density + 0.5f);
    }

    private TextView text(String message, int size, int color) {
        TextView view = new TextView(this);
        view.setText(message);
        view.setTextSize(size);
        view.setTextColor(color);
        view.setPadding(0, dip(9), 0, dip(9));
        return view;
    }

    private String supportedAbis() {
        if (Build.VERSION.SDK_INT >= 21) {
            String[] abis = Build.SUPPORTED_ABIS;
            if (abis != null && abis.length > 0) {
                StringBuilder out = new StringBuilder();
                for (String abi : abis) {
                    if (out.length() > 0) out.append(", ");
                    out.append(abi);
                }
                return out.toString();
            }
        }
        return Build.CPU_ABI == null ? "unknown" : Build.CPU_ABI;
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll = new ScrollView(this);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setBackgroundColor(Color.WHITE);
        column.setPadding(dip(22), dip(18), dip(22), dip(18));
        column.addView(text("Revibe installation test", 25, Color.rgb(20, 79, 110)));
        column.addView(text("This independent Android app has installed and opened.", 17, Color.rgb(17, 104, 63)));
        column.addView(text("Android " + Build.VERSION.RELEASE
            + " (API " + Build.VERSION.SDK_INT + ")", 16, Color.BLACK));
        column.addView(text("Supported OS architectures: " + supportedAbis(), 14, Color.DKGRAY));
        column.addView(text("Not Messenger: this diagnostic cannot log in to Facebook or send messages.", 17, Color.DKGRAY));
        column.addView(text("Optional: choose an existing Messenger APK to learn why Android rejects it. Android still asks you to approve installation. We never replace an installed Messenger.", 15, Color.DKGRAY));
        choose = new Button(this);
        choose.setText("Choose an APK to test");
        choose.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) { startChooser(); }
        });
        column.addView(choose);
        if (Build.VERSION.SDK_INT >= 26) {
            Button permission = new Button(this);
            permission.setText("Allow install permission (only if required)");
            permission.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View view) { showInstallerPermissionSettings(); }
            });
            column.addView(permission);
        }
        status = text(InstallerState.lastResult(this), 16, Color.rgb(0, 73, 115));
        column.addView(status);
        Button copyResult = new Button(this);
        copyResult.setText("Copy result");
        copyResult.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) {
                // Copy only the category we store, never a URI, device ID or raw log.
                ClipboardManager clipboard =
                    (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard == null) return;
                clipboard.setPrimaryClip(ClipData.newPlainText(
                    "Revibe install result", InstallerState.lastResult(MainActivity.this)));
                Toast.makeText(MainActivity.this,
                    "Error category copied", Toast.LENGTH_SHORT).show();
            }
        });
        column.addView(copyResult);
        column.addView(text("Privacy: no internet permission, no contacts, chat data or uploads. Results stay on this phone.", 13, Color.DKGRAY));
        scroll.addView(column);
        setContentView(scroll);
    }

    @Override protected void onResume() {
        super.onResume();
        InstallerState.attach(this);
        if (status != null) status.setText(InstallerState.lastResult(this));
    }

    @Override protected void onPause() {
        InstallerState.detach(this);
        super.onPause();
    }

    public void showResultFromReceiver(final String result) {
        runOnUiThread(new Runnable() {
            @Override public void run() { if (status != null) status.setText(result); }
        });
    }

    private void tell(String message) {
        InstallerState.setResult(this, message);
    }

    private void startChooser() {
        if (Build.VERSION.SDK_INT < 21) {
            tell("On Android 4.4, detailed package-install error reports are unavailable. No APK was installed.");
            return;
        }
        if (Build.VERSION.SDK_INT >= 26 && !getPackageManager().canRequestPackageInstalls()) {
            tell("Android needs permission before this app can request package installation. Use the permission button, then select the APK again.");
            return;
        }
        Intent pick = new Intent(Intent.ACTION_GET_CONTENT);
        pick.setType("application/vnd.android.package-archive");
        pick.addCategory(Intent.CATEGORY_OPENABLE);
        try {
            startActivityForResult(Intent.createChooser(pick, "Select a Messenger test APK"), CHOOSE_APK);
        } catch (ActivityNotFoundException error) {
            tell("No Android file picker available. Nothing was installed.");
        }
    }

    private void showInstallerPermissionSettings() {
        if (Build.VERSION.SDK_INT < 26) return;
        try {
            Intent settings = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                Uri.parse("package:" + getPackageName()));
            startActivity(settings);
        } catch (ActivityNotFoundException error) {
            tell("The Android installation-permission screen is not available.");
        }
    }

    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != CHOOSE_APK || result != RESULT_OK || data == null
                || data.getData() == null) return;
        final Uri uri = data.getData();
        choose.setEnabled(false);
        tell("Checking the selected file. Nothing installed yet.");
        new Thread(new Runnable() {
            @Override public void run() { processSelectedApk(uri); }
        }, "revibe-local-apk-check").start();
    }

    private boolean isAlreadyInstalled(String packageName) {
        try {
            getPackageManager().getPackageInfo(packageName, 0);
            return true;
        } catch (PackageManager.NameNotFoundException expected) {
            return false;
        }
    }

    private void processSelectedApk(Uri uri) {
        File copy = new File(getCacheDir(), "temporary-selected.apk");
        try {
            MessageDigest sha256 = MessageDigest.getInstance("SHA-256");
            InputStream source = getContentResolver().openInputStream(uri);
            if (source == null) throw new IllegalStateException("APK cannot be read");
            try {
                FileOutputStream target = new FileOutputStream(copy);
                try {
                    byte[] buffer = new byte[65536];
                    long total = 0;
                    int n;
                    while ((n = source.read(buffer)) != -1) {
                        total += n;
                        if (total > APK_LIMIT) throw new IllegalArgumentException("APK larger than limit");
                        target.write(buffer, 0, n);
                        sha256.update(buffer, 0, n);
                    }
                } finally { target.close(); }
            } finally { source.close(); }

            PackageInfo info = getPackageManager().getPackageArchiveInfo(copy.getAbsolutePath(), 0);
            if (info == null || info.packageName == null) {
                tell("Android could not parse this APK. No install attempted.");
                return;
            }
            String pkg = info.packageName;
            if (!"com.facebook.orca".equals(pkg) && !"org.revibe.orca01".equals(pkg)) {
                tell("Only known Messenger research APKs can be tested. Nothing installed.");
                return;
            }
            if (!AllowedApks.matches(pkg, AllowedApks.hex(sha256.digest()))) {
                tell("Selected APK does not match an audited research test file. Nothing installed.");
                return;
            }
            if (isAlreadyInstalled(pkg)) {
                tell("Messenger is already installed; it was preserved and no replacement attempted.");
                return;
            }
            tell("APK accepted for testing. Waiting for Android's installation result.");
            SessionHelper.commit(this, copy);
        } catch (Exception error) {
            // Never expose the content URI, local paths, account data or raw errors.
            tell("Could not start the install test (" + error.getClass().getSimpleName()
                + "). Success has not been confirmed.");
        } finally {
            if (copy.exists()) copy.delete();
            runOnUiThread(new Runnable() {
                @Override public void run() { choose.setEnabled(true); }
            });
        }
    }
}