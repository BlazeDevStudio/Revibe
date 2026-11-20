package org.revibe.installprobe;
import android.content.pm.PackageInstaller;
/** Never expose raw system error messages: only safe installation categories. */
public final class InstallStatus {
    private InstallStatus() {}
    public static String category(int status) {
        switch (status) {
            case PackageInstaller.STATUS_SUCCESS: return "Installed successfully";
            case PackageInstaller.STATUS_PENDING_USER_ACTION: return "Waiting for Android installation approval";
            case PackageInstaller.STATUS_FAILURE_ABORTED: return "Installation cancelled";
            case PackageInstaller.STATUS_FAILURE_BLOCKED: return "Installation blocked by device policy or security";
            case PackageInstaller.STATUS_FAILURE_CONFLICT: return "Package or signing conflict";
            case PackageInstaller.STATUS_FAILURE_INCOMPATIBLE: return "APK not compatible with this Android system";
            case PackageInstaller.STATUS_FAILURE_INVALID: return "APK rejected as invalid";
            case PackageInstaller.STATUS_FAILURE_STORAGE: return "Not enough installation storage";
            case PackageInstaller.STATUS_FAILURE: return "Installation failed (general error)";
            default: return "Installation returned unrecognized status " + status;
        }
    }
    public static String failureCode(String raw) {
        if (raw == null) return "";
        java.util.regex.Matcher matcher = java.util.regex.Pattern
            .compile("\\bINSTALL_(?:FAILED|PARSE_FAILED)_[A-Z0-9_]+\\b").matcher(raw);
        return matcher.find() ? matcher.group() : "";
    }
}
