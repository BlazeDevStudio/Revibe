package org.revibe.foundation;

/**
 * Fail-closed boundary. No Meta user authentication, transport, token exchange,
 * or E2EE protocol is authorized or implemented for this third-party client.
 * Do not enable by changing a boolean: replacing this gate requires real
 * protocol source, eligibility evidence, and live end-to-end verification.
 */
public final class BackendGate {
    private BackendGate() {}

    public static boolean isPersonalMessengerInteroperabilityAvailable() {
        return false;
    }

    public static String stateCode() {
        return "BLOCKED_META_PERSONAL_INTEROPERABILITY";
    }

    /** Forbidden until an approved, independently verified transport is wired. */
    public static void beginPersonalMessengerSession() {
        throw new UnsupportedOperationException(
            "Personal Messenger integration not authorized or implemented");
    }
}
