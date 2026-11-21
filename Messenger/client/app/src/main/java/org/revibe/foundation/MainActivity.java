package org.revibe.foundation;

import android.app.Activity;
import android.graphics.Color;
import android.os.Build;
import android.os.Bundle;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * Native, screen-reader-accessible Android compatibility foundation.
 * NOT Messenger; intentionally no fake conversations, fake authentication,
 * WebView, private backend, input of credentials, or delivery indicators.
 */
public final class MainActivity extends Activity {
    private int dp(int pixels) {
        return (int) (pixels * getResources().getDisplayMetrics().density + 0.5f);
    }

    private void addText(LinearLayout parent, String label, int sp, int color) {
        TextView text = new TextView(this);
        text.setText(label);
        text.setTextSize(sp);
        text.setTextColor(color);
        text.setPadding(0, dp(12), 0, dp(12));
        text.setImportantForAccessibility(TextView.IMPORTANT_FOR_ACCESSIBILITY_YES);
        parent.addView(text, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    @Override public void onCreate(Bundle savedState) {
        super.onCreate(savedState);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.WHITE);

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(24), dp(32), dp(24), dp(24));
        content.setBackgroundColor(Color.WHITE);

        addText(content, "REVIBE — CLIENT FOUNDATION", 26, Color.rgb(10, 59, 87));
        addText(content, "Personal Messenger connection is unavailable.", 23,
            Color.rgb(128, 31, 18));
        addText(content,
            "This independent Android program cannot sign in to Facebook, "
            + "read Messenger conversations or send messages. "
            + "No personal Messenger service connection has been authorized.",
            20, Color.BLACK);
        addText(content,
            "There is no chat screen, password field, or hidden messaging service. "
            + "No messages can be delivered by this build.",
            18, Color.DKGRAY);
        addText(content,
            "Build state: " + BackendGate.stateCode(), 16, Color.DKGRAY);
        addText(content,
            "Android " + Build.VERSION.RELEASE + " (API " + Build.VERSION.SDK_INT + ")",
            16, Color.DKGRAY);
        scroll.addView(content);
        setContentView(scroll);
    }
}
