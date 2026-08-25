# Intercom API

Base URL when used through HTTPS: `/intercom/api`

## Health

`GET /api/health`

## Announcements

- `GET /api/announcements`
- `POST /api/announcements` multipart form: `label`, `audio`
- `POST /api/announcements/{id}/audio` replace audio
- `POST /api/announcements/{id}/toggle`
- `DELETE /api/announcements/{id}`
- `POST /api/announcements/{id}/play`
- `GET /api/announcements/{id}/audio`
- `GET /api/enabled`

## Settings

- `GET /api/settings`
- `POST /api/settings` JSON: `{ "announcement_volume": 70 }`

## Receiver power

- `GET /api/receiver-power`
- `POST /api/receiver-power/toggle`

## LIVE

- `POST /api/live/start` JSON: `{ "sample_rate": 48000 }`
- `POST /api/live/{session_id}/audio` body: raw mono signed 16-bit PCM
- `POST /api/live/{session_id}/stop`
- `GET /api/live/status`
