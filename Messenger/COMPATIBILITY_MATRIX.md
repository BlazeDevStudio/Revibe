# Compatibility and acceptance matrix

Target matrix only; not a claim of release support.

| Android version | API | ARMv7 | ARM64 | x86 |
|---|---:|---|---|---|
| 4.4 | 19 | original 410 static gate passes; runtime untested | untested (OS hardware constraints) | untested |
| 5 | 21 | untested | untested | original 410 static minimum supported; runtime untested |
| 6 | 23 | untested | untested | untested |
| 7 | 24/25 | untested | untested | untested |
| 8 | 26/27 | untested | untested | untested |
| 9 | 28 | untested | original 588 minimum supported; runtime untested | untested |
| 10 | 29 | untested | untested | untested |

All `Revibe` builds must pass installation, visible UI launch, authorized account login, real encrypted message sending, reception/decryption, background notifications, reconnection and accessibility/usability checks before distribution. A static gate or successful installer is insufficient.

Three ABI variants are a packaging objective, not an output of Stages 1–4.
