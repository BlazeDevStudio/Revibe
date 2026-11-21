package org.revibe.foundation;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Real, offline, non-sensitive elder-friendly accessibility setting.
 * Does not store account data, identifiers, messages or service credentials.
 */
public final class AccessibilitySettings {
    private static final String STORE = "revibe_accessibility";
    private static final String LARGE_TEXT = "extra_large_text";

    private AccessibilitySettings() {}

    public static boolean isExtraLarge(Context context) {
        return context.getSharedPreferences(STORE, Context.MODE_PRIVATE)
            .getBoolean(LARGE_TEXT, false);
    }

    public static void setExtraLarge(Context context, boolean large) {
        SharedPreferences.Editor edit = context.getSharedPreferences(
            STORE, Context.MODE_PRIVATE).edit();
        edit.putBoolean(LARGE_TEXT, large);
        // Commit synchronously before rerender; single boolean only.
        if (!edit.commit()) {
            throw new IllegalStateException("Cannot save accessibility setting");
        }
    }
}
