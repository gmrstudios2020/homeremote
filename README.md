# Whole House AV Remote + Intercom

A self-hosted LAN remote for a Sony STR-ZA1100ES based AV system with TV/Blu-ray controls, prerecorded whole-house announcements, browser recording, and live microphone intercom routed through a UGREEN NAS, HDMI, Sony Zone 2, and a Sonance multi-channel amplifier.

This repository is the cleaned, documented version of a working home deployment. Device addresses, TV PSKs, certificates, MAC addresses, and saved recordings are intentionally excluded from Git.

## Start here if your hardware is different

Do not copy the reference IP addresses, HDMI sink, audio GID, SAT/CATV routing, or other machine-specific values blindly. The project now includes a discovery-first setup path that walks through your own topology before deployment.

Start with [Setup Guide](docs/SETUP-GUIDE.md), then fill out the [Setup Worksheet](docs/SETUP-WORKSHEET.md). See [Compatibility and Adaptation](docs/COMPATIBILITY.md) and [Receiver Adaptation](docs/RECEIVER-ADAPTATION.md) if your hardware differs from the reference system.

The goal is to reproduce the behavior, not Gerard's exact wiring or network values.

## What it does

- Sony-style responsive browser remote
- Receiver power, inputs, and state polling
- Sony TV control through the TV JSON/IRCC APIs
- Sony Blu-ray control plus Wake-on-LAN
- Dynamic Intercom tab populated from enabled announcements
- Prerecorded whole-house announcements played three times
- Upload or record announcement audio from the browser
- LIVE microphone intercom from a phone/browser
- Shared Intercom volume control
- Automatic intercom routing through MAIN SAT/CATV plus Zone 2 SAT
- Automatic restoration of the previous main receiver input after an announcement or LIVE session
- HTTPS reverse proxy so browser microphone APIs work
- Persistent announcement recordings/configuration outside the container image

## Tested topology

```text
Phone / browser
      |
      | HTTPS
      v
 remote.home :443
      |
      +---- / ------------------> Sony Remote :8088
      |
      +---- /intercom/ ----------> Intercom :8089
                                      |
                                      v
                              UGREEN PulseAudio
                                      |
                                    HDMI
                                      |
                               Sony STR receiver
                                      |
                                Zone 2 analog out
                                      |
                                Sonance BUS input
                                      |
                               Whole-house speakers
```

The intercom implementation temporarily switches the receiver MAIN zone to SAT/CATV because this particular receiver only passed the UGREEN HDMI source to the Zone 2 analog output when MAIN was also on SAT/CATV. The previous MAIN input is restored after playback.

## Repository layout

```text
.
├── .env.example
├── remote/
│   ├── index.html
│   ├── nginx.conf.template
│   ├── wol_server.py
│   ├── Dockerfile.remote
│   ├── Dockerfile.wol
│   └── docker-compose.yaml
├── intercom/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── docker-compose.yaml
│   ├── templates/index.html
│   └── PERSISTENT_DATA.md
├── reverse-proxy/
│   ├── nginx.conf.template
│   ├── docker-compose.yaml
│   └── certs/
└── docs/
```

## Quick start

1. Read [Setup Guide](docs/SETUP-GUIDE.md).
2. Complete [Setup Worksheet](docs/SETUP-WORKSHEET.md).
3. Copy `.env.example` to `.env` and enter values you actually verified.
4. Deploy Intercom first and test the complete physical audio path.
5. Deploy the web remote and test each device integration independently.
6. Configure local DNS and HTTPS only after the HTTP services work.
7. Test browser recording and LIVE last.

For a close match to the reference hardware, see [Installation](docs/INSTALLATION.md). For a different receiver or wiring topology, see [Compatibility and Adaptation](docs/COMPATIBILITY.md).

## Persistent data

`intercom/data/` is intentionally ignored by Git. It contains user recordings and settings and must survive upgrades. Do not replace that directory when updating application code.

## Security

Never commit `.env`, your Sony TV PSK, certificate private keys, Blu-ray MAC address if you consider it private, or recorded household announcements. See [Security](docs/SECURITY.md).

## Project status

Known-good baseline includes prerecorded announcements, browser recording, LIVE intercom, intercom volume, HTTPS, and receiver input restoration.

## Trademark notice

Sony and Sonance are trademarks of their respective owners. This is an independent home automation project and is not affiliated with or endorsed by Sony, Sonance, UGREEN, or Ubiquiti.

## License

No open-source license is granted by default. See `LICENSE`.
