package org.revibe.installprobe;

/** Offline allowlist of byte-for-byte audited research artifacts.
 * No network, no device identifiers and no signing keys are needed.
 * These checks are for install diagnostics, NOT for Meta server eligibility.
 */
public final class AllowedApks {
    private AllowedApks() {}

    static String hex(byte[] bytes) {
        final char[] chars = "0123456789abcdef".toCharArray();
        char[] result = new char[bytes.length * 2];
        for (int i = 0; i < bytes.length; i++) {
            result[2 * i] = chars[(bytes[i] >>> 4) & 0x0f];
            result[2 * i + 1] = chars[bytes[i] & 0x0f];
        }
        return new String(result);
    }

    static boolean matches(String packageName, String sha256) {
        if (packageName == null || sha256 == null || sha256.length() != 64) return false;
        if ("com.facebook.orca".equals(packageName)) {
            return "70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab".equals(sha256)
                || "006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8".equals(sha256)
                || "7e1a128728935ca3b9afd4079a7018b31c00b6215067514dfee8adc6ca5e66dd".equals(sha256);
        }
        if ("org.revibe.orca01".equals(packageName)) {
            return "4eaf15fe989b62c51f86a5145d848f12fe63ccef581ee0d6c5ffd964b4a9b1ec".equals(sha256);
        }
        return false;
    }
}
