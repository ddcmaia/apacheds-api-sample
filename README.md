# ApacheDS + Flask Api Demo

This project demonstrates an ApacheDS server with a Flask API to perform CRUD operations on users and groups.

## Running

```bash
docker compose up --build
```

The API will be available at `http://localhost:5034`.

## Project structure

- `apacheds/` – Dockerfile and configuration files for ApacheDS.
- `app/` – Flask application with CRUD routes.
- `docker-compose.yml` – Orchestrates the two services.

