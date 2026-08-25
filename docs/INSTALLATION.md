# Installation

> If your receiver, NAS audio stack, HDMI input, or Zone 2 routing differs from the reference system, complete [SETUP-GUIDE.md](SETUP-GUIDE.md) first. This page is the shortest path for installations that are already close to the tested topology.

## Requirements

- Docker / Docker Compose on the NAS
- A Linux host audio stack exposing PulseAudio at `/var/run/pulse/native`
- HDMI output from the NAS to the receiver
- Sony STR receiver reachable over LAN
- Sony TV with network control enabled and a pre-shared key
- Optional Sony Blu-ray player with network control and Wake-on-LAN
- Local DNS capable of resolving the chosen hostname to the NAS
- HTTPS certificate trusted by the phone/browser for microphone features

## 1. Configure environment

From the repository root:

```sh
cp .env.example .env
```

Edit `.env`. Do not commit it.

Important values are `NAS_HOST`, `AVR_HOST`, `TV_HOST`, `TV_PSK`, `BDP_HOST`, `BDP_MAC`, `LAN_BROADCAST`, and `PULSE_SINK`.

## 2. Verify the NAS HDMI sink

On the NAS, identify the PulseAudio sink:

```sh
pactl list short sinks
```

The tested deployment used an HDMI sink similar to:

```text
alsa_output.pci-0000_0c_00.1.hdmi-stereo-extra1
```

Set `PULSE_SINK` in `.env` to the exact sink on your host.

## 3. Deploy Intercom

```sh
cd intercom
docker compose --env-file ../.env up -d --build
```

Verify:

```sh
curl http://127.0.0.1:8089/api/health
```

The `data/` directory will be created locally and mounted to `/data`. Keep it permanently.

## 4. Deploy the Remote

```sh
cd ../remote
docker compose --env-file ../.env up -d --build
```

Verify the remote at `http://NAS_IP:8088`.

## 5. Local DNS

Create an A record on your LAN DNS server:

```text
remote.home -> NAS_IP
```

`.home` is used here because it was the preferred local naming scheme for the tested deployment. Avoid `.local` if your network relies heavily on mDNS/Bonjour.

## 6. HTTPS

Follow [HTTPS.md](HTTPS.md), then deploy:

```sh
cd ../reverse-proxy
docker compose --env-file ../.env up -d
```

Open:

```text
https://remote.home
```

The Intercom settings page is available at:

```text
https://remote.home/intercom/
```

## 7. Receiver / Sonance signal path

The tested signal path is:

```text
UGREEN HDMI -> Sony STR SAT/CATV -> Zone 2 analog L/R -> Sonance BUS input
```

Configure the Sonance BUS/DIP switches for the desired channels. This repository does not modify physical Sonance amplifier settings.

## Updating

Back up `intercom/data/` before major changes. Application upgrades should replace code and images only, never user data.
