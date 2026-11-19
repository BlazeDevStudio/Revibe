# Messenger Android 4.4 — Stage 3 Engineering Package

**Not a Messenger application or replacement APK.** This is a verified static analysis and device-preflight toolkit to guide legitimate compatibility research. It does not contain any Meta APK, code output from Superpack, native library binary, account, password, message, or personal log.

## Requirements

- Python 3.8+ standard library
- Three original APKs (not bundled): Messenger v410 API19 ARMv7, v410 API21 x86, v588 API28 ARM64
- Optional: `readelf` to list native ELF dependencies
- Optional: `adb` to perform local authorized Android 4.4 device tests

## One-command static report

```bash
python run_stage3.py --apk-dir "/folder/with/original/apks" --output-dir results
python -m unittest discover -s tests -v
```

The command generates five JSON documents (`summary.json`, class comparison, metadata, native library interfaces, and Android 4.4 preflight). It does not install or execute anything from any APK.

## Individual tools

- `android44_apk_preflight.py` — evaluate minimum SDK, native CPU ABI, and old Android signature artifact for any APK. For ARM KitKat: `python android44_apk_preflight.py "your.apk" --api 19 --abis armeabi-v7a,armeabi`
- `dex_class_matrix.py` — DEX class-definition overlap, app namespace counts, and E2EE-related symbol-name markers (standard DEX only).
- `cross_variant_spo.py` — compare SHA-1 locator metadata across archives.
- `superpack_native_surface.py` — identify native JNI bridge strings, ELF architecture, and optional dependency list.
- `inspect_superpack.py` — Stage 2 Superpack file table and independent XZ inventory; **not** a full decoder.
- `kitkat_device_probe.py` — authorized ADB device inventory and *optional* install/launch of original user-owned APK.
- `messenger_log_sieve.py` — bounded Messenger-process logcat error categories, no raw text in outputs. Example: `python messenger_log_sieve.py --adb --output messenger_errors.json`
- `dex_api_inventory.py` — Stage 2 framework method-name reference inventory.
- `compare_410_variants.py` — Stage 2 SHA-1 matching by secondary DEX ordinal.
- `apk_static_audit.py` — Stage 1 binary Android manifest parser reused for install preflight.

## Privacy and interpretation

Do not share raw logcat captures or authentication data. Static APK compatibility is not proof of current login or end-to-end encrypted messaging. No cryptographic bypass or credential proxying is performed. All APK originals remain unchanged.

See `MILESTONE_3_MESSENGER_ANDROID44.md` for the results and next engineering decision gate.
