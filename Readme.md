# FastAPI Calculator

Simple, reliable calculator API and UI built with FastAPI. Supports addition, subtraction, multiplication, and division with clean logging, typed operations, and full test coverage (unit, integration, and Playwright E2E).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-✨-teal)
![Pytest](https://img.shields.io/badge/tests-pytest-green)
![Playwright](https://img.shields.io/badge/E2E-Playwright-8A2BE2)
![CI](https://github.com/Vishesh0-7/Calculator_FastAPI/actions/workflows/ci.yml/badge.svg?branch=main)


## Features

- FastAPI service with endpoints for add, sub, mul, div, and a generic calc router
- Static HTML UI at `/` for quick manual testing
- Auto-generated API docs at `/docs` (Swagger) and `/redoc`
- Robust tests: unit, integration, and E2E (Playwright)
- GitHub Actions CI running tests on every push/PR to `main`


## Quickstart

Prerequisites:
- Python 3.8+
- pip

Clone and set up:

```bash
git clone https://github.com/Vishesh0-7/Calculator_FastAPI.git
cd calculator--FastApi

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies and browsers for Playwright
pip install -r requirements.txt
playwright install
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Open in your browser:
- UI: http://127.0.0.1:8000/
- Docs (Swagger): http://127.0.0.1:8000/docs
- Docs (ReDoc): http://127.0.0.1:8000/redoc


## API Reference

All endpoints accept query parameters and return JSON.

- GET `/health`
	- Response: `{ "status": "ok" }`

- GET `/add?a=<float>&b=<float>` → `{ "result": number }`
- GET `/sub?a=<float>&b=<float>` → `{ "result": number }`
- GET `/mul?a=<float>&b=<float>` → `{ "result": number }`
- GET `/div?a=<float>&b=<float>` → `{ "result": number }` or `400 { "detail": "Division by zero" }`

- GET `/calc?op=<add|sub|mul|div>&a=<float>&b=<float>`
	- Success: `{ "op": string, "result": number }`
	- Errors: `400 { "detail": "Unsupported operation" }` or `400 { "detail": "Division by zero" }`

Examples:

```bash
curl "http://127.0.0.1:8000/add?a=3&b=2"
curl "http://127.0.0.1:8000/calc?op=mul&a=4&b=2.5"
```


## Project Structure

```
calculator--FastApi/
├── app/
│   ├── main.py           # FastAPI app, routes, logging, static mount
│   ├── operations.py     # Calculator operations (add, sub, mul, div)
│   └── static/
│       └── index.html    # Simple UI for manual testing
├── tests/
│   ├── unit/             # Unit tests for operations
│   ├── integration/      # API endpoint tests using TestClient
│   └── e2e/              # Playwright UI tests (spawns uvicorn)
├── requirements.txt
├── pytest.ini
├── Readme.md
└── .github/workflows/ci.yml
```


## Testing

Run the full test suite:

```bash
pytest -q
```

Run specific groups:

```bash
# Unit + integration
pytest tests/unit tests/integration -q

# End-to-end (starts a local server on :8000)
pytest tests/e2e -q
```

Note: For E2E tests, ensure Playwright browsers are installed:

```bash
playwright install
```


## Continuous Integration (CI)

GitHub Actions runs on pushes/PRs to `main`:
- Install dependencies and Playwright browsers
- Run unit and integration tests
- Run Playwright E2E tests

Workflow file: `.github/workflows/ci.yml`.


## Development notes

- Logging is configured in `app/main.py`; adjust level/format as needed.
- Static assets are served from `app/static` at `/static` (UI uses `/` route for convenience).
- The operations are implemented in `app/operations.py` with simple, typed functions.


## License

This project is licensed under the MIT License.

See the LICENSE file for details.


## Acknowledgements

- FastAPI for the excellent web framework
- Playwright for smooth browser automation

