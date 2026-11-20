package org.revibe.installprobe;

import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.graphics.Color;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/**
 * A real, independent APK for checking Revibe's installation pipeline.
 * No internet permission, no account login, no telemetry, no Meta SDK.
 * Do not represent this as a Messenger or messaging client.
 */
public final class MainActivity extends Activity {
    private int dip(int dp) {
        return (int) (dp * getResources().getDisplayMetrics().density + 0.5f);
    }

    private TextView text(String value, int size, int color) {
        TextView v = new TextView(this);
        v.setText(value);
        v.setTextSize(size);
        v.setTextColor(color);
        v.setPadding(0, dip(8), 0, dip(8));
        return v;
    }

    private String osAbis() {
        if (Build.VERSION.SDK_INT >= 21) {
            String[] values = Build.SUPPORTED_ABIS;
            if (values != null && values.length > 0) {
                StringBuilder s = new StringBuilder();
                for (String abi : values) {
                    if (s.length() > 0) s.append(", ");
                    s.append(abi);
                }
                return s.toString();
            }
        }
        return Build.CPU_ABI == null ? "unavailable" : Build.CPU_ABI;
    }

    @Override
    public void onCreate(Bundle savedState) {
        super.onCreate(savedState);
        ScrollView scroll = new ScrollView(this);
        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setBackgroundColor(Color.WHITE);
        column.setPadding(dip(20), dip(20), dip(20), dip(20));

        column.addView(text("Revibe installation works", 24, Color.rgb(16, 96, 60)));
        column.addView(text("This device was able to install and launch an independently built Revibe APK.", 17, Color.DKGRAY));
        column.addView(text("Android: " + Build.VERSION.RELEASE
            + " (API " + Build.VERSION.SDK_INT + ")", 16, Color.BLACK));
        column.addView(text("Android-supported ABIs: " + osAbis(), 15, Color.BLACK));
        column.addView(text("Package: org.revibe.installprobe", 14, Color.DKGRAY));
        column.addView(text("This is a diagnostic application only. It does not log into Facebook, send messages, use Meta services or read your accounts.", 15, Color.DKGRAY));
        column.addView(text("It requests no permissions and has no network access.", 14, Color.DKGRAY));

        Button close = new Button(this);
        close.setText("Close");
        close.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View view) {
                finish();
            }
        });
        column.addView(close);
        scroll.addView(column);
        setContentView(scroll);
    }
}
