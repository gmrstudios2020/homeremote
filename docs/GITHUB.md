# Publishing to GitHub

The repository archive is already structured for GitHub and excludes runtime recordings, secrets, and certificate keys.

## Before the first push

1. Review `.env.example` and confirm it contains examples only.
2. Do not add your real `.env` file.
3. Do not add anything from `intercom/data/`.
4. Do not add TLS private keys from `reverse-proxy/certs/`.
5. Decide whether to keep the included all-rights-reserved `LICENSE` or replace it with an open-source license.

## Command-line upload

```sh
git init
git add .
git commit -m "Initial known-good release"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

## GitHub web upload

Create an empty repository, unzip this package, and upload the contents of `whole-house-av-remote/` so `README.md` is at the repository root.

## Suggested repository description

> Self-hosted Sony AV remote and whole-house Sonance intercom with UGREEN HDMI audio, browser recording, LIVE microphone streaming, and HTTPS.

## Suggested topics

`home-automation`, `sony`, `sonance`, `ugreen`, `docker`, `nginx`, `flask`, `intercom`, `av`, `self-hosted`
