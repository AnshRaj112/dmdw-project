ML Services (Python 3.9.13)

This FastAPI service exposes:
- GET /health
- POST /parse_resume (multipart file upload)
- POST /recommend (JSON payload)

Backend expects ML_SERVICE_URL to point here (default http://localhost:8000).

Prerequisites
- Python 3.9.13
- pip

Setup (Windows)
```bash
# From repo root
cd ml-services

# Ensure Python 3.9.13 is used
python --version

# Create venv (optional)
python -m venv .venv

# Activate
. .venv/Scripts/activate

# Install deps
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Environment
- Backend reads `ML_SERVICE_URL` (see `backend/env.example`). Default is `http://localhost:8000`.

Example payloads
- interests:
```json
{ "interests": ["data-science", "ai-ml"], "type": "interests" }
```
- resume:
```json
{
  "skills": [],
  "interests": ["data-science"],
  "experience": [],
  "projects": [],
  "education": [],
  "location": "Remote",
  "type": "resume"
}
```

Notes
- Companies list is in `data/companies.txt`.
- Scoring is a lightweight keyword overlap; replace with your model later.

