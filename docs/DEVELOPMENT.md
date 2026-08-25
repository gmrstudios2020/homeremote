# Development notes

## Known-good principle

This system grew around tested receiver behavior. Preserve working infrastructure and make the smallest possible change. Do not reconstruct an existing Compose file from memory when modifying a deployed system.

## Remote UI changes

The current known-good deployment bakes `remote/index.html` into the nginx image. After changing the file, rebuild with `--no-cache` and force-recreate the container.

## Intercom UI changes

`intercom/templates/` is bind-mounted into the Intercom container. UI-only changes generally require replacing the template and restarting the container if the NAS replaces the file inode rather than editing it in place.

## Backend changes

Rebuild the Intercom image when changing `app.py`, Python dependencies, or the Dockerfile.

## Persistent data

Never place generated `intercom/data/` contents into release archives. Treat that directory as user data, not application source.
