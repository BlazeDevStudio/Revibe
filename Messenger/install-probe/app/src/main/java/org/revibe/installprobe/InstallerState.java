package org.revibe.installprobe;
import android.content.Context;
import java.lang.ref.WeakReference;
/** Records only a local, generic result category. No device IDs or messages. */
public final class InstallerState {
    private static WeakReference<MainActivity> foreground = new WeakReference<>(null);
    private InstallerState() {}
    public static void attach(MainActivity activity) { foreground = new WeakReference<>(activity); }
    public static void detach(MainActivity activity) {
        if (foreground.get() == activity) foreground.clear();
    }
    public static void setResult(Context context, String status) {
        context.getSharedPreferences("revibe_install_test", Context.MODE_PRIVATE)
            .edit().putString("last_status", status).apply();
        MainActivity open = foreground.get();
        if (open != null) open.showResultFromReceiver(status);
    }
    public static String lastResult(Context context) {
        return context.getSharedPreferences("revibe_install_test", Context.MODE_PRIVATE)
            .getString("last_status", "No package-manager result yet.");
    }
}
