# Architecture

## Components

### Remote web app

A static HTML/CSS/JavaScript interface served by nginx. It talks to the receiver, TV, and Blu-ray through same-origin nginx proxy routes so browser code does not need direct device access.

### Blu-ray WOL helper

A tiny Python HTTP service using host networking so it can emit a LAN broadcast magic packet.

### Intercom backend

A Flask service that stores announcement metadata/audio, normalizes uploads with ffmpeg, controls the Sony receiver, and sends audio to the host PulseAudio HDMI sink with `paplay`.

### HTTPS reverse proxy

A small nginx service on host port 443. It exposes the remote at `/` and the Intercom app at `/intercom/` under one secure origin.

## Why MAIN SAT/CATV is switched

Testing on the STR-ZA1100ES showed that setting only `zone2.input=sat` did not physically route the NAS HDMI audio into the Zone 2 analog output. When the receiver MAIN input was manually switched to SAT/CATV, the same Intercom playback worked.

The backend therefore temporarily sets both the MAIN zone and Zone 2 route for intercom use and restores MAIN afterward.

## LIVE audio transport

The browser captures mono microphone audio through the Web Audio API, converts Float32 samples to signed 16-bit PCM, and POSTs small chunks to the Intercom backend. The backend pipes the PCM stream into a long-running `paplay --raw` process connected to the HDMI PulseAudio sink.
