# ApacheDS + Flask Demo

This project demonstrates an ApacheDS server with a Flask API to perform CRUD operations on users and groups.

## Features

- Hierarchical groups where all groups use the `GG_` prefix; groups without a parent act as top-level containers for other `GG_` groups.
- Group ownership stored in a custom `groupOwner` attribute is inherited from parent groups if a group's owner is removed, ensuring every group has an owner.
- Endpoint to assign a specific user as a group's owner.
- Group owners must also be members of their group. When a user is moved out of a group they own, ownership is transferred to the parent group's owner and the user becomes only a member of the new group.
- Actions are audited and written to `audit.log`. Enable `ENABLE_AUDIT_BUCKET` and set `AUDIT_BUCKET` to upload this file to a Google Cloud Storage bucket.
- Deleting a user via the API removes them from all groups, sets `accountStatus=inactive`, and moves the entry to a dedicated `Desativados` OU instead of removing the record entirely.

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
- `architecture.md` – Diagrams outlining the group and user hierarchy.
- `docker-compose.yml` – Orchestrates the two services.

