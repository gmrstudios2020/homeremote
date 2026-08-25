# HTTPS and browser microphone access

Browser microphone APIs require a secure context on typical mobile browsers. The remote therefore uses a local HTTPS reverse proxy.

## Local certificate with mkcert

On Windows:

```powershell
winget install --id FiloSottile.mkcert -e
mkcert -install
mkdir C:\remote-cert
cd C:\remote-cert
mkcert remote.home
```

Copy the resulting certificate and key into `reverse-proxy/certs/` and name them:

```text
server.pem
server-key.pem
```

The private key must never be committed to Git.

`mkcert -install` trusts the local CA on the computer where it is run. Other phones/tablets may need the mkcert root CA installed and explicitly trusted if you want the browser to show a fully trusted connection without warnings.

## Port 443

The reverse proxy uses host port 443. If the NAS management UI already owns 443, disable only its optional port-443 redirect or otherwise free 443 without changing the NAS management HTTPS port.

Verify availability with:

```sh
ss -tlnp | grep ':443 '
```

## Routes

```text
https://remote.home/           -> 127.0.0.1:8088
https://remote.home/intercom/  -> 127.0.0.1:8089
```

Keeping both apps behind one HTTPS origin avoids mixed-content and CORS problems.
