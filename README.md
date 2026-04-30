## Secure Flask REST API
A REST API for managing Projects, built with Flask. Features JWT authentication, role-based access control, HTTPS, and request logging.



## Setup

### 1. Install dependencies

```bash
pip install flask flask-jwt-extended
```

### 2. Generate a self-signed certificate (for HTTPS)

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=localhost"
```

This creates `cert.pem` and `key.pem` in  project folder.

### 3. Run the server

```bash
python app.py
```

The API is now available at `https://localhost:5000`.

---

## Authentication

All endpoints (except `/login`) require a JWT Bearer token.


### Test accounts

| Username | Password    | Role  |
|----------|-------------|-------|
| admin    | password123 | admin |
| user     | password123 | user  |

---

## Endpoints

### Projects

| Method | Endpoint               | Role          | Description             |
|--------|------------------------|---------------|-------------------------|
| GET    | `/projects`            | user or admin | List all projects       |
| POST   | `/projects`            | admin         | Create a new project    |
| PUT    | `/projects/<id>`       | admin         | Update a project        |
| DELETE | `/projects/<id>`       | admin         | Delete a project        |

### Logs

| Method | Endpoint | Role          | Description              |
|--------|----------|---------------|--------------------------|
| GET    | `/logs`  | admin         | View last 20 log entries |

---

## Example requests (curl)

All curl examples disable SSL verification (`-k`) because using a self-signed certificate.

**Login:**
```bash
curl -k -X POST https://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

**List projects (replace TOKEN):**
```bash
curl -k https://localhost:5000/projects \
  -H "Authorization: Bearer TOKEN"
```

**Create a project:**
```bash
curl -k -X POST https://localhost:5000/projects \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Project Three", "description": "New project"}'
```

**Update a project:**
```bash
curl -k -X PUT https://localhost:5000/projects/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Renamed Project One"}'
```

**Delete a project:**
```bash
curl -k -X DELETE https://localhost:5000/projects/3 \
  -H "Authorization: Bearer TOKEN"
```

**View logs (admin only):**
```bash
curl -k https://localhost:5000/logs \
  -H "Authorization: Bearer TOKEN"
```

---

## Logging

All requests are automatically logged to `api.log` in JSON format:

```json
{"timestamp": "2025-04-24T10:23:01Z", "ip": "127.0.0.1", "method": "GET", "path": "/projects", "status": 200}
```

Failed login attempts are also logged as warning events with the attempted username.
