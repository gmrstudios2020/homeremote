# Contributing

This repository represents a working home deployment with device-specific behavior. Contributions are welcome as patches or forks, but changes should avoid breaking the known-good Sony STR / UGREEN / Sonance path.

Before submitting changes:

1. Do not include private `.env` values, PSKs, certificates, recordings, or device credentials.
2. Preserve persistent-data semantics.
3. Test both prerecorded playback and LIVE start/stop routing.
4. Verify the receiver returns to the previous MAIN input after Intercom use.
5. Document any device-specific assumptions.
