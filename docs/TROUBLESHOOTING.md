# Troubleshooting

## `paplay ... returned non-zero exit status 1`

Check PulseAudio connectivity inside the Intercom container. The tested fix was to mount the entire PulseAudio directory:

```yaml
- /var/run/pulse:/var/run/pulse
```

Mounting only `/var/run/pulse/native` can leave the container attached to a stale Unix socket if PulseAudio recreates it.

## `Connection failure: Connection refused` from PulseAudio

Compare host/container socket visibility and confirm `PULSE_SERVER=unix:/var/run/pulse/native` and the exact sink from `pactl list short sinks`.

## Browser recording says microphone is unsupported

Use HTTPS. An HTTP LAN IP generally is not a secure browser context for `getUserMedia()`.

## `405 Method Not Allowed` from the Intercom settings page

Make sure the page is opened through `/intercom/` and API calls are relative so they resolve beneath that prefix. The included settings page already uses relative API paths.

## `items.sort is not a function`

This previously occurred when the settings UI accidentally requested the remote app instead of `/intercom/api/announcements`. The current page uses relative URLs and validates the response before sorting.

## Zone 2 says SAT but there is no announcement audio

On the tested STR-ZA1100ES, Zone 2 state reporting `sat` was not enough. The receiver MAIN zone also had to be on SAT/CATV to pass the NAS HDMI signal to Zone 2 analog out. Current backend code handles this automatically.

## Sony remote rebuild shows an older HTML file

Force a no-cache image rebuild:

```sh
docker compose build --no-cache sony-remote
docker compose up -d --force-recreate sony-remote
```

## nginx returns 403 with a bind-mounted UI file on a NAS

NAS ACLs can prevent nginx UID 101 from reading bind-mounted files even when the path appears readable inside the container. The known-good deployment bakes `index.html` into the remote image rather than bind-mounting it.

## Blu-ray status returns 502

This usually means the Blu-ray player is off, asleep, or its Sony control service is not answering. Wake it first and verify `BDP_HOST`.
