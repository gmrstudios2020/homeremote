# Compatibility and Adaptation

HomeRemote is not a universal AV control protocol. It is a working Sony-based implementation designed so the hardware-specific parts are identifiable and replaceable.

## Tested reference system

The reference deployment used:

- Linux-based UGREEN NAS
- Docker Compose
- PulseAudio-compatible host socket
- NAS HDMI output
- Sony STR-ZA1100ES receiver
- Sony network-controlled TV
- Sony Blu-ray player
- Receiver Zone 2 analog output
- Sonance distribution amplifier BUS input

These are reference components, not values everyone should copy.

## What is broadly reusable

Docker deployment, the browser UI, HTTPS reverse proxy, announcement storage, browser recording, LIVE PCM transport, ffmpeg normalization, PulseAudio output, persistent data, and the local DNS approach are broadly reusable.

## What is Sony-specific

The current implementation uses Sony `/request.cgi`, `main.input`, `zone2.input`, `GUI.*` receiver features, Sony TV JSON/IRCC APIs, and Sony Blu-ray IRCC/status endpoints.

## What is installation-specific

Expect IP addresses, subnet, broadcast address, HDMI sink, audio group GID, hostname, TV PSK, Blu-ray MAC, receiver HDMI input, Zone 2 behavior, HDMI lock timing, and amplifier wiring to differ.

## Receiver-free HDMI-to-RCA topology

The Sony receiver is not fundamentally required to turn the NAS audio into something a whole-house amplifier can use. If you only need analog line-level audio, an HDMI audio extractor can replace the receiver layer:

```text
NAS HDMI -> HDMI audio extractor -> stereo RCA -> distribution amplifier / mixer / powered input
```

A recommended reference device is the **StarTech HD202A HDMI Audio Extractor**. It provides stereo RCA analog output, optical output, 2-channel EDID selection, and HDMI pass-through:

https://www.startech.com/en-us/audio-video-products/hd202a

Use 2-channel PCM stereo for the normal HomeRemote audio path.

If the HDMI source may output Dolby/DTS or other multichannel formats, choose an extractor that explicitly supports stereo downmixing. The **OREI HDA-913** is one example:

https://www.orei.com/products/orei-hdmi-18gbps-audio-extractor-with-audio-downmix-hda-913

This topology is attractive when the distribution amplifier already has an unused stereo RCA, AUX, or BUS input. It removes the receiver's input switching and Zone 2 behavior from the physical audio path.

The current reference backend still performs Sony receiver-control calls before and after playback. A receiver-free installation therefore needs those calls bypassed or adapted. The browser UI, announcement storage, recording, LIVE PCM stream, `paplay` HDMI output, volume control, HTTPS, and persistent data do not inherently require the receiver.

## Adapting another Sony STR model

Start by testing:

```text
main.input
zone2.power
zone2.input
```

Determine which feature physically selects the HDMI input. Set `INTERCOM_INPUT` for the Zone 2 source. If the MAIN zone must use something other than SAT/CATV, adapt the receiver mapping in `intercom/app.py`. Do not assume all Sony receivers expose identical values.

## Adapting another server or NAS

You need Docker or an equivalent environment, a host audio device that can send sound to the receiver or extractor, a PulseAudio-compatible interface for the current backend or a replacement audio backend, and permission for the container to access it. UGREEN-specific UI steps are not required by the software itself.

## Adapting another distribution amplifier

HomeRemote does not directly control the Sonance amplifier in the reference deployment. Any distribution amplifier can work if it accepts the upstream analog output and routes it to the desired zones. Amplifiers requiring API control, muting, triggers, or per-zone switching need an additional integration.

## Adapting another receiver brand

A new adapter needs equivalent operations for reading and setting the main input, powering the secondary zone, selecting its source, and restoring the previous input. Replace the Sony-specific backend calls and nginx proxy routes, and document the platform-specific behavior.

Alternatively, if the receiver is only being used to convert the NAS HDMI signal to analog audio, consider eliminating that dependency entirely with the receiver-free HDMI audio extractor topology above.
