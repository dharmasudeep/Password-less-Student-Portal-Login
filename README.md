# Password-less Chat

A production-ready Flask application featuring secure email/password authentication, a polished chat UI backed by a local Ollama LLM, and an extensible architecture prepared for upcoming face-recognition features.

## Features

- ✅ User registration, login, and logout with PBKDF2 password hashing and Flask-Login sessions
- ✅ CSRF protection, security headers, and per-IP rate limiting on chat APIs
- ✅ Responsive, accessible templates with mobile-first design, dark-mode support, and keyboard navigation
- ✅ Chat interface supporting both full-response and streaming modes when connected to a local Ollama instance
- ✅ Admin dashboard for viewing registered users and CLI utilities for promotion and maintenance
- ✅ SQLAlchemy ORM models with SQLite defaults (configurable via `DATABASE_URL`)
- ✅ Comprehensive tests for auth and chat flows (Ollama mocked)
- ✅ Placeholder blueprint for future face-recognition APIs (not yet implemented)

## Quick start

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -e .[dev]
   ```

3. **Copy environment defaults and update values**
   ```bash
   cp .env.example .env
   ```
   Adjust `SECRET_KEY`, `OLLAMA_MODEL`, and any other sensitive settings.

4. **Run database migrations (or initialize tables)**
   ```bash
   flask db upgrade  # or flask shell -c "from app.extensions import db; db.create_all()"
   ```

5. **Start the application**
   ```bash
   flask run
   ```

Visit [http://localhost:5000](http://localhost:5000) to register and begin chatting.

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Flask environment | `development` |
| `SECRET_KEY` | Session/signing secret | Required |
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite:///instance/app.db` |
| `OLLAMA_HOST` | Base URL for the local Ollama server | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model name passed to Ollama | `llama3` |
| `RATE_LIMIT` | Limit for `/api/chat*` endpoints | `30/minute` |

## Local Ollama setup

1. Install and run [Ollama](https://ollama.com/). Ensure it listens on `http://localhost:11434` (default).
2. Pull the model defined in `OLLAMA_MODEL`, for example:
   ```bash
   ollama pull llama3
   ```
3. Confirm the API is reachable before starting the Flask app:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Streaming mode

The chat UI includes a "Streaming" toggle. When enabled, `/api/chat/stream` proxies Ollama's streaming responses via Server-Sent Events. Disable it to fall back to standard JSON responses.

## Admin tools

- Navigate to `/admin/users` as an admin to view registered users.
- Promote an existing user (or create one) via CLI:
  ```bash
  flask create-admin user@example.com
  ```
- View all users:
  ```bash
  flask list-users
  ```
- Clear chat history:
  ```bash
  flask clear-messages
  ```

## Docker

A sample compose file is provided to run both the Flask app and Ollama:

```bash
docker compose up -d
# After the Ollama container is running, pull your model:
docker exec -it password-less-ollama-1 ollama pull llama3
```

The `web` service uses Gunicorn on port `8000`. Update environment variables in `.env` or pass them via `docker compose` overrides. Remember to expose the same `OLLAMA_MODEL` used by the chat app.

## Security notes

- Passwords are stored using Werkzeug's PBKDF2 hashing.
- CSRF protection is enforced globally via Flask-WTF.
- Responses include basic security headers and a strict Content Security Policy.
- Rate limiting (default `30/minute`) is applied to chat endpoints to mitigate abuse.
- Sessions use `HttpOnly` cookies with SameSite=Lax.

## Troubleshooting

- **Ollama not running:** Ensure `OLLAMA_HOST` is reachable. The app will return a 503 JSON error if Ollama cannot be contacted.
- **Streaming stuck:** Verify the browser can reach the Ollama endpoint and that the model is downloaded. Toggle streaming off to fall back to standard responses.
- **CSRF errors:** Confirm the `<meta name="csrf-token">` is present and that requests include the `X-CSRFToken` header. Clearing cookies and re-authenticating can resolve stale sessions.
- **Database permission errors:** The default SQLite file lives under `instance/app.db`. Ensure the directory is writable by the running process.

## Testing

Run unit tests with:
```bash
pytest -q
```
Tests mock the Ollama client, so no network access is required.

## Face recognition roadmap

Face recognition is not implemented yet. A dedicated `face` blueprint currently exposes `/face/status` returning `{ "implemented": false }` with TODO placeholders indicating where enrollment and verification endpoints will be added in the future.
