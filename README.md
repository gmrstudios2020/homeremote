# Whole House AV Remote + Intercom

A self-hosted LAN remote for a Sony STR-ZA1100ES based AV system with TV/Blu-ray controls, prerecorded whole-house announcements, browser recording, and live microphone intercom routed through a UGREEN NAS, HDMI, Sony Zone 2, and a Sonance multi-channel amplifier.

This repository is the cleaned, documented version of a working home deployment. Device addresses, TV PSKs, certificates, MAC addresses, and saved recordings are intentionally excluded from Git.

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

1. Copy `.env.example` to `.env` and enter your device addresses, TV PSK, Blu-ray MAC, LAN broadcast address, and PulseAudio sink.
2. Copy or symlink the same `.env` into each service directory, or run Compose with `--env-file ../.env`.
3. Deploy `intercom/` first and confirm `http://NAS_IP:8089/api/health` returns `{"ok":true,...}`.
4. Deploy `remote/` and confirm `http://NAS_IP:8088` loads the remote.
5. Create a local DNS record such as `remote.home -> NAS_IP`.
6. Generate/install a trusted local certificate and place the certificate and key in `reverse-proxy/certs/` using the filenames documented in `docs/HTTPS.md`.
7. Deploy `reverse-proxy/` and use `https://remote.home`.

See [Installation](docs/INSTALLATION.md) for the complete procedure.

Ready to publish? See [Publishing to GitHub](docs/GITHUB.md).

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
