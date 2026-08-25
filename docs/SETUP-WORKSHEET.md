# Setup Worksheet

Fill this out before changing configuration. It is intentionally hardware-neutral.

## Network

```text
NAS / Docker host IP:
Receiver IP:
TV IP:
Blu-ray IP:
Subnet:
LAN broadcast:
Chosen local hostname:
```

## Server audio

```text
Operating system / NAS platform:
Docker / Compose version:
PulseAudio, PipeWire, or other:
Pulse server socket:
HDMI sink name:
Audio group GID:
```

Commands that may help:

```sh
pactl info
pactl list short sinks
id
ls -l /var/run/pulse/native
```

## Receiver

```text
Brand:
Model:
Control URL:
Main input used by server HDMI:
API feature used to select that input:
Zone 2 input:
Zone 2 output type:
Fixed or variable Zone 2 level:
Does MAIN also need to be on the HDMI input?:
Approximate input lock delay:
```

## Physical signal path

```text
Server output:
Receiver input:
Receiver output:
Distribution amplifier input:
Speaker zones:
```

Example only:

```text
NAS HDMI -> SAT/CATV -> Zone 2 RCA -> amplifier BUS -> ceiling speakers
```

## TV

```text
Brand:
Model:
IP control enabled:
Authentication type:
PSK configured:
```

## Blu-ray / media player

```text
Brand:
Model:
IP:
MAC:
Network control protocol:
Wake-on-LAN supported:
```

## Intercom test results

```text
Server test tone reaches receiver:
Receiver routes source to whole-house amplifier:
Zone 2 powers on correctly:
MAIN must switch:
Configured MAIN input:
Configured Zone 2 input:
Announcement playback works:
Previous MAIN input restores:
Browser recording works over HTTPS:
LIVE microphone works:
```

## Notes

Record model-specific quirks here. These details are valuable for future compatibility documentation and pull requests.
