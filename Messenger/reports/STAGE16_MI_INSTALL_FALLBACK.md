# Stage 16 — Mi installation failure and original ARM32 fallback

The user reports that the Revibe Stage15 **side-by-side** ARM64 APK also shows **App not installed** on a Mi phone. That falsifies the hypothesis that merely changing the package ID resolves installation. The phone OS ABI and exact Android package-manager error remain unknown. Never claim installation success based on ZIP/signature checks.

## Genuine alternative for an Android 5/6 phone with a possibly 32-bit OS
- Original Meta-signed Messenger **410.0.0.17.85**: **Android 4.4/API19**, `armeabi-v7a` (ARM32); original APK SHA256 `006ca274cf2a2569cf8e5c68c94c2317377c6406957fe4e4daedc0436ee790c8`.
- Original Meta-signed Messenger **336.0.0.13.142**: Android 5/API21, `arm64-v8a`; original SHA256 `70b1eeb59866900a245b4c15cde557757ba457b2a60c69a7275d05c7bc5a1aab`.
- Both originals use the same Meta certificate fingerprint `e3f9e1e0cf99d0e56a055ba65e241b3399f7cea524326b0cdd6ec1327ed0fdc1`.
- Original 410 is **not** the earlier re-signed Revibe 410 trial: no code or strings were edited, and the Meta signature remains intact.

A phone marketed with a 64-bit CPU may still run a 32-bit Android OS. If its supported OS ABI list includes only `armeabi-v7a`, the original ARM32 APK meets basic SDK/ABI requirements whereas the native ARM64 APK does not. This has not been confirmed for this particular Mi phone.

### Build-free, simple installation
A verified original ARM32 test APK can be tapped from Downloads, with no computer, ADB or special installer. This is only an alternate hypothesis-driven test. The user may still see `App not installed` due to storage, existing package/version, OS security policy, ABI or other device restrictions. Never ask them to uninstall important data or disable protections.

### Source tooling
`Messenger/engineering/prepare_original_abi_candidate.py` verifies the pinned original APK, native ABI, ZIP integrity and Java v1 signature; then copies it byte-for-byte. Does not modify or re-sign Meta code. Use `--variant arm32-api19` or `--variant arm64-api21`. Proprietary APKs and keys are never committed to public GitHub.

## Remaining blockers
Real Android installation not verified; Meta login, updated transport, modern E2EE and notifications not repaired. Continue from this field result; do not confuse an install candidate with restored service.
