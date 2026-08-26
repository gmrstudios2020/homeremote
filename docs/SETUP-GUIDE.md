# Setup Guide: Adapt HomeRemote to Your System

HomeRemote started as one working installation, but the repository is intended to be adapted. Do not begin by copying the tested IP addresses, HDMI input, PulseAudio sink, audio GID, or receiver assumptions. First inventory your own system.

Complete [SETUP-WORKSHEET.md](SETUP-WORKSHEET.md) as you go.

## 1. Draw your signal path

Write down how audio should travel from the server to the speakers.

Reference installation:

```text
NAS HDMI -> Sony receiver SAT/CATV -> Zone 2 analog output -> Sonance BUS input -> whole-house speakers
```

Your HDMI input and amplifier can differ. The important requirement is that the server can deliver audio to an input that can ultimately feed the whole-house amplifier.

### Receiver-free option: HDMI audio extractor

You do not have to use an AV receiver as the HDMI-to-analog bridge.

A simpler intercom-only signal path can be:

```text
NAS HDMI -> HDMI audio extractor -> stereo RCA -> distribution amplifier / mixer / powered input -> speakers
```

A solid reference choice is the **StarTech HD202A HDMI Audio Extractor**. It accepts HDMI, provides dual-RCA analog stereo output plus optical audio, supports 2-channel EDID selection, and also provides HDMI pass-through if you need it later:

https://www.startech.com/en-us/audio-video-products/hd202a

For HomeRemote intercom audio, configure the extractor/source for **2-channel PCM stereo**. The NAS is already producing ordinary PCM audio, so you do not need surround decoding for the normal announcement/LIVE path.

If your source may send Dolby/DTS or other multichannel bitstreams, use an extractor with an explicit stereo downmixer instead of assuming every HDMI-to-RCA box can decode them. One example is the OREI HDA-913, which advertises analog stereo downmixing:

https://www.orei.com/products/orei-hdmi-18gbps-audio-extractor-with-audio-downmix-hda-913

This can be especially useful if you already have a whole-house amplifier with an unused BUS/AUX/RCA input and only need to turn the NAS HDMI audio into line-level analog audio.

Important: the current reference backend includes Sony receiver routing because that is how the original installation works. A receiver-free deployment should bypass or adapt those receiver-control steps so audio playback does not depend on a Sony receiver being reachable. The HDMI audio generation, announcements, LIVE streaming, volume control, HTTPS, and persistent-data pieces are otherwise still useful.

## 2. Decide how close your hardware is

If you have a Linux Docker host with PulseAudio-compatible audio, HDMI to a Sony STR receiver using `/request.cgi`, and Zone 2 feeding a distribution amplifier, setup should mostly be configuration.

A similar Sony receiver with different input behavior may require adapting the receiver routing. A different receiver brand requires a new control adapter. A receiver-free HDMI-extractor path can remove the receiver from the audio chain entirely, but the reference backend's receiver-control calls must then be bypassed or adapted. See [COMPATIBILITY.md](COMPATIBILITY.md).

## 3. Find and stabilize device addresses

Record the NAS, receiver, TV, and optional Blu-ray IP addresses. DHCP reservations are recommended for infrastructure devices.

From Windows you can verify basic reachability with:

```powershell
Test-Connection 192.168.1.50 -Count 2
```

Use your real address. Ping only proves network reachability, not that the device control API is enabled.

## 4. Verify the receiver API first

For compatible Sony STR models, query `main.input` before installing HomeRemote:

```powershell
$body = @{
    type = "http_get"
    packet = @(@{ id = 100; feature = "main.input" })
} | ConvertTo-Json -Depth 6

Invoke-WebRequest `
    -Uri "http://YOUR_RECEIVER_IP/request.cgi" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body |
    Select-Object -ExpandProperty Content
```

If this fails, solve receiver IP control before deploying the application.

If you are deliberately using the receiver-free HDMI-extractor topology, skip receiver API discovery and instead verify the extractor produces clean stereo RCA audio from the NAS HDMI source.

## 5. Identify the server HDMI input

Do not assume SAT/CATV. Connect the server HDMI output to the receiver and record the actual input used.

For a receiver-free setup, connect the server HDMI output to the extractor and verify its RCA output instead.

## 6. Test Zone 2 manually

Play a test sound from the server and manually establish the whole-house route. Determine:

1. Whether Zone 2 must be powered on
2. Which Zone 2 input exposes the server audio
3. Whether MAIN must also be on the same input
4. How long the receiver takes to lock onto HDMI audio
5. Whether the Zone 2 output is fixed or variable level

The reference STR-ZA1100ES required MAIN on SAT/CATV and Zone 2 on SAT. Setting only `zone2.input=sat` was not enough. Your receiver may differ.

If you are using a receiver-free extractor, replace this step with a direct test of the extractor's RCA output into the amplifier/mixer input.

See [RECEIVER-ADAPTATION.md](RECEIVER-ADAPTATION.md).

## 7. Find and test the server audio sink

On the Linux host:

```sh
pactl list short sinks
```

Identify the HDMI/DisplayPort sink connected to the receiver or HDMI extractor. Test it directly before installing HomeRemote:

```sh
paplay --device=YOUR_SINK test.wav
```

If audio does not reach the receiver/extractor here, fix the host audio path first.

If your host uses PipeWire, confirm its PulseAudio compatibility layer exposes working `pactl`, `paplay`, and the socket used by the container.

## 8. Determine audio permissions

Run:

```sh
id
ls -l /var/run/pulse/native
```

Set `AUDIO_GID` to the group the container needs for host audio access. The reference UGREEN host used GID 10, but that is not universal.

## 9. Configure optional TV and Blu-ray integrations

The current TV integration is Sony-specific and expects Sony network control with a pre-shared key. The tested Blu-ray integration uses Sony IRCC plus Wake-on-LAN.

If your devices differ, treat those as optional integrations and adapt or remove their routes rather than copying settings that do not apply.

## 10. Create `.env`

From the repository root:

```sh
cp .env.example .env
```

Enter only values you have actually verified. Never commit `.env`.

See [CONFIGURATION.md](CONFIGURATION.md).

## 11. Deploy Intercom first

```sh
cd intercom
docker compose --env-file ../.env up -d --build
```

Check:

```sh
curl http://127.0.0.1:8089/api/health
```

Create one announcement and use PLAY HOUSE. On the reference receiver topology, verify that the receiver saves the current MAIN input, establishes the correct whole-house route, plays audio, and restores the previous MAIN input. Do not continue until this works.

For a receiver-free topology, first adapt/bypass the receiver-control portion of the backend, then verify the announcement reaches the extractor's RCA output and your amplifier.

## 12. Deploy the remote

```sh
cd ../remote
docker compose --env-file ../.env up -d --build
```

Open:

```text
http://YOUR_NAS_IP:8088
```

Test each device integration independently.

## 13. Add local DNS and HTTPS

Browser microphone recording and LIVE intercom require a secure browser context. Choose a local hostname, point it at the NAS, and follow [HTTPS.md](HTTPS.md).

The reference installation used `remote.home`; you can choose another hostname.

## 14. Test recording and LIVE

From the HTTPS address, grant microphone permission, record and save a short announcement, play it through the house, then test LIVE start and stop. On receiver-based deployments, verify that the receiver returns to its previous MAIN input afterward.

## 15. Protect persistent data

Recordings and announcement configuration live under:

```text
intercom/data/
```

Treat this as user data. Application updates should replace code, not `intercom/data/`. See [PERSISTENT_DATA.md](../intercom/PERSISTENT_DATA.md).

## When asking for help

Include the receiver model if used, TV model, NAS/server OS, Docker version, intended signal path, `pactl list short sinks`, a sanitized `.env`, relevant container logs, what works manually, and the exact point where automated behavior differs.

Never post passwords, PSKs, private certificate keys, or other secrets.
