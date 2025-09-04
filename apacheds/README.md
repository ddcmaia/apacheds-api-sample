# ApacheDS Container

This directory contains a lightweight ApacheDS LDAP server image with optional replication support.

## Layout
- `Dockerfile` – builds the container image.
- `bin/entrypoint.sh` – main entrypoint script that configures the server, loads LDIF files and launches ApacheDS in the foreground.
- `bin/replica-check.sh` – background helper that keeps replication targets in sync with Marathon.
- `lib/replication.sh` – shared helper functions for replication tasks.
- `files/`, `ldifs/` and `templates/` – supporting scripts, LDIF seeds and configuration templates.

The image expects environment variables such as `ADMIN_PASSWORD`, `DOMAIN_NAME` and `DOMAIN_SUFFIX`. See the entrypoint script for available options.
