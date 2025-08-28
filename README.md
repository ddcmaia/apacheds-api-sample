# ApacheDS + Flask Demo

This project demonstrates an ApacheDS server with a Flask API to perform CRUD operations on users and groups.

## Features

- Hierarchical groups where `GU_` prefixed groups can contain `GG_` groups.
- Group ownership stored in a custom `groupOwner` attribute is inherited from parent groups if a group's owner is removed, ensuring every group has an owner.
- Endpoint to assign a specific user as a group's owner.
- Actions are audited and written to `audit.log`. Enable `ENABLE_AUDIT_BUCKET` and set `AUDIT_BUCKET` to upload this file to a Google Cloud Storage bucket.

## Running

```bash
docker compose up --build
```

The API will be available at `http://localhost:5034`.

## Audit log upload

Set the `ENABLE_AUDIT_BUCKET` environment variable to `true` and `AUDIT_BUCKET` to the name of a Google Cloud Storage bucket. With credentials configured (for example, via `GOOGLE_APPLICATION_CREDENTIALS`), the application uploads `audit.log` to this bucket after each action.

## Project structure

- `apacheds/` – Dockerfile and configuration files for ApacheDS.
- `app/` – Flask application with CRUD routes.
- `docker-compose.yml` – Orchestrates the two services.

