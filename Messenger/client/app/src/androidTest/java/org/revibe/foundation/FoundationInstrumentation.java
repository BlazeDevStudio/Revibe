package org.revibe.foundation;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;

/**
 * On-emulator tests assert a truthful blocked UI and absence of sensitive
 * permissions. Does not test Meta authentication, chats, or cryptography.
 */
public final class FoundationInstrumentation extends Instrumentation {
    private int checks;

    private void require(boolean good, String description) {
        if (!good) throw new AssertionError(description);
        checks++;
    }

    private String allText(View view) {
        StringBuilder out = new StringBuilder();
        collect(view, out);
        return out.toString();
    }

    private void collect(View view, StringBuilder out) {
        if (view instanceof TextView) {
            out.append(((TextView) view).getText()).append("\n");
        }
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) {
                collect(group.getChildAt(i), out);
            }
        }
    }

    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        start();
    }

    @Override public void onStart() {
        Bundle result = new Bundle();
        Activity activity = null;
        try {
            String packageId = getTargetContext().getPackageName();
            require("org.revibe.client.foundation".equals(packageId),
                "Foundation app ID may not impersonate product release");
            PackageInfo info = getTargetContext().getPackageManager()
                .getPackageInfo(packageId, PackageManager.GET_PERMISSIONS);
            String[] perms = info.requestedPermissions;
            require(perms == null || perms.length == 0,
                "No sensitive permissions permitted in blocked foundation");
            require(!BackendGate.isPersonalMessengerInteroperabilityAvailable(),
                "Meta connectivity must be disabled without authorization");
            require("BLOCKED_META_PERSONAL_INTEROPERABILITY".equals(BackendGate.stateCode()),
                "State must match machine-readable blocker");

            boolean rejected = false;
            try {
                BackendGate.beginPersonalMessengerSession();
            } catch (UnsupportedOperationException expected) {
                rejected = true;
            }
            require(rejected, "Unauthorized session must fail closed");

            Intent launch = new Intent(Intent.ACTION_MAIN);
            launch.setClassName(packageId, "org.revibe.foundation.MainActivity");
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            activity = startActivitySync(launch);
            waitForIdleSync();
            require(activity != null, "Native activity must launch");
            String text = allText(activity.getWindow().getDecorView());
            require(text.contains("connection is unavailable"),
                "Cannot show a fake connected state");
            require(text.contains("No messages can be delivered"),
                "Must warn that messaging is not implemented");
            require(!text.contains("Enter password"),
                "No credential collection controls");
            final Button enlarge = (Button) activity.findViewById(MainActivity.ID_LARGER_TEXT);
            require(enlarge != null, "Real large-text control required");
            runOnMainSync(new Runnable() {
                @Override public void run() { enlarge.performClick(); }
            });
            require(AccessibilitySettings.isExtraLarge(getTargetContext()),
                "Large-text choice must persist in private settings");
            final Button normal = (Button) activity.findViewById(MainActivity.ID_STANDARD_TEXT);
            require(normal != null, "Standard text control required");
            runOnMainSync(new Runnable() {
                @Override public void run() { normal.performClick(); }
            });
            require(!AccessibilitySettings.isExtraLarge(getTargetContext()),
                "Standard-text choice must persist");
            result.putString("stream", "PASS: " + checks
                + " on-emulator foundation assertions (NO Meta messaging tested)");
            finish(0, result);
        } catch (Exception error) {
            result.putString("stream", "FAIL: " + error.getClass().getSimpleName());
            finish(-1, result);
        } catch (AssertionError error) {
            result.putString("stream", "FAIL: " + error.getMessage());
            finish(-1, result);
        } finally {
            if (activity != null) activity.finish();
        }
    }
}
