package org.revibe.installprobe;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageInstaller;
import android.os.Build;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;
/** Android 5/API21+ only; requires explicit user selection and no existing target. */
public final class SessionHelper {
    private SessionHelper() {}
    public static void commit(Context context, File apk) throws Exception {
        PackageInstaller installer = context.getPackageManager().getPackageInstaller();
        PackageInstaller.SessionParams params = new PackageInstaller.SessionParams(
            PackageInstaller.SessionParams.MODE_FULL_INSTALL);
        int sessionId = installer.createSession(params);
        PackageInstaller.Session session = null;
        boolean committed = false;
        try {
            session = installer.openSession(sessionId);
            InputStream source = new FileInputStream(apk);
            OutputStream target = null;
            try {
                target = session.openWrite("base.apk", 0, apk.length());
                byte[] buffer = new byte[65536];
                int count;
                while ((count = source.read(buffer)) != -1) target.write(buffer, 0, count);
                session.fsync(target);
            } finally {
                try { if (target != null) target.close(); }
                finally { source.close(); }
            }
            Intent response = new Intent(context, InstallResultReceiver.class);
            response.setAction("org.revibe.installprobe.RESULT");
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            // Android 15 requires a mutable IntentSender for installer session responses.
            if (Build.VERSION.SDK_INT >= 31) flags |= PendingIntent.FLAG_MUTABLE;
            PendingIntent result = PendingIntent.getBroadcast(context, sessionId, response, flags);
            session.commit(result.getIntentSender());
            committed = true;
        } finally {
            if (session != null) session.close();
            if (!committed) installer.abandonSession(sessionId);
        }
    }
}
