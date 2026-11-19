# Revibe

Revibe is an independent AI-assisted software preservation and accessibility project to help aging apps and refurbished devices remain useful. The first project is **Messenger**.

- [Messenger engineering and current status](Messenger/CONTINUATION.md)
- [Verified status (machine-readable)](Messenger/STATUS.json)
- [Contributor/agent instructions](AGENTS.md)
- [Session initialization script](scripts/revibe_init.py)

**Current status: no functioning Messenger replacement or release yet.** Stage 6 provides a locally reproducible API19/ARMv7 research APK which changes two UI strings only. It is not verified to run on-device, authenticate, send messages, or suppress a real mandatory version gate.

Run `python scripts/revibe_init.py --check` for next-session handoff and offline tests. Revibe is independent and is not affiliated with or endorsed by Meta.