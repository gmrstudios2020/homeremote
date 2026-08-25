# Configuration reference

All private deployment values belong in `.env`.

| Variable | Purpose |
| --- | --- |
| `NAS_HOST` | NAS LAN address |
| `REMOTE_PORT` | Local HTTP port for the remote, default 8088 |
| `INTERCOM_PORT` | Local HTTP port for Intercom, default 8089 |
| `WOL_PORT` | Host-network Wake-on-LAN helper port, default 8090 |
| `AVR_HOST` | Sony STR receiver address |
| `INTERCOM_INPUT` | Zone 2 source key, tested as `sat` |
| `TV_HOST` | Sony TV address |
| `TV_PSK` | Sony TV pre-shared key |
| `BDP_HOST` | Sony Blu-ray address |
| `BDP_MAC` | Blu-ray MAC for Wake-on-LAN |
| `LAN_BROADCAST` | LAN broadcast address used for WOL |
| `PULSE_SINK` | PulseAudio HDMI sink on the NAS |
| `AUDIO_GID` | Host audio group GID, tested as 10 |
| `REMOTE_HOSTNAME` | Local HTTPS hostname, e.g. `remote.home` |

## Announcement behavior

Prerecorded announcements:

1. Save current receiver MAIN input.
2. Switch MAIN to SAT/CATV.
3. Turn Zone 2 on.
4. Set Zone 2 input to SAT.
5. Wait for HDMI/Zone 2 routing to lock.
6. Play the announcement three times.
7. Turn Zone 2 off.
8. Restore the prior MAIN input.

LIVE follows the same routing sequence and restores the receiver when the session stops.

## Announcement volume

The configured percentage is applied to `paplay` before the signal leaves the NAS. It does not modify the Sonance gain structure or normal receiver listening volume.
