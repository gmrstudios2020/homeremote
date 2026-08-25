# Persistent intercom data

The running container mounts `./data` to `/data`.

This directory contains:

- `announcements.json`
- `settings.json`
- `audio/*.wav`

It is intentionally excluded from Git. Never replace or delete it during upgrades. Back it up before changing storage paths or moving the installation.
