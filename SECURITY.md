# Security

This project is designed for a trusted home LAN. It is not hardened for direct Internet exposure.

## Do not commit

- `.env`
- Sony TV PSK
- certificate private keys
- saved announcements and recordings
- any credentials or tokens

The repository `.gitignore` excludes the expected sensitive paths.

## HTTPS

HTTPS is primarily required here to provide a secure browser context for microphone recording/LIVE intercom. The included reverse proxy terminates TLS locally.

## Network exposure

Keep device-control endpoints on the LAN. Do not port-forward 8088, 8089, 8090, or 443 to the public Internet without adding authentication, authorization, rate limits, and broader hardening.

## LIVE microphone

The remote visibly changes state while LIVE is active and automatically stops LIVE when navigating away from the Intercom tab. Audio is streamed for playback and is not intentionally persisted by the LIVE endpoints.
