# InfraPilot

AI-assisted infrastructure drift detection for Terraform and Kubernetes. InfraPilot combines a React dashboard, a FastAPI backend, local/cloud AI providers, rule-based fallbacks, Oumi severity scoring, and Cline-powered patch generation.

## What It Does

- Analyzes Terraform and Kubernetes manifests for drift, misconfiguration, security risks, and operational anti-patterns.
- Supports local Ollama models, Gemini cloud models, Oumi integrations, and a rule-engine fallback when AI is unavailable.
- Produces a drift score, timeline forecast, issue list, severity labels, Oumi scores, and fix suggestions.
- Provides an authenticated dashboard with a chat-style analysis workflow.
- Can optionally email analysis results through SMTP.
- Can generate and apply unified diff patches through the AutoFix/Cline integration.

## Tech Stack

- Frontend: React 19, TypeScript, Vite, React Router, Tailwind CSS, Framer Motion, lucide-react, Recharts, Three.js
- Backend: FastAPI, Pydantic, SQLAlchemy, SQLite, JWT auth, bcrypt, python-jose
- AI providers: Ollama, Gemini, Oumi, Oumi RL scorer
- Automation: Cline workflow scripts for patch generation and patch application

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         React + Vite Frontend                      │
│                                                                    │
│  Home Page        Login/Register        Protected Dashboard         │
│     │                  │                       │                    │
│     │                  │                       ├─ Paste/attach IaC  │
│     │                  │                       ├─ Select file type  │
│     │                  │                       ├─ Select AI model   │
│     │                  │                       └─ Optional email    │
└─────┴──────────────────┴───────────────────────┬────────────────────┘
                                                   │ HTTP/JSON
                                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                          FastAPI Backend                           │
│                                                                    │
│  main.py                                                           │
│   ├─ CORS middleware                                               │
│   ├─ /auth router                                                  │
│   ├─ /analyze endpoint                                             │
│   └─ /autofix router                                               │
│                                                                    │
│  Auth Layer                                                        │
│   ├─ Email/password registration                                   │
│   ├─ JWT token login                                               │
│   └─ SQLite users table                                            │
│                                                                    │
│  Analyzer Service                                                  │
│   ├─ Provider/model selection                                      │
│   ├─ AI full-file analysis                                         │
│   ├─ Terraform/Kubernetes rule fallback                            │
│   ├─ Oumi RL issue scoring                                         │
│   └─ Drift score + timeline response                               │
│                                                                    │
│  Optional Email Service                                            │
│   └─ SMTP result delivery after /analyze returns                    │
└───────────────────────────────┬────────────────────────────────────┘
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
      ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
      │ Ollama Local   │ │ Gemini Cloud │ │ Oumi / RL    │
      │ localhost:11434│ │ API key      │ │ API/scoring  │
      └────────────────┘ └──────────────┘ └──────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                         AutoFix Path                               │
│                                                                    │
│  /autofix/generate ──► ClineAgent ──► Cline workflow/script         │
│          │                                │                         │
│          ▼                                ▼                         │
│   Unified diff patch              scripts/run_cline.sh              │
│          │                                                          │
│          ▼                                                          │
│  /autofix/apply ─────► scripts/apply_patch.sh ─────► target file    │
└────────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. A user registers or logs in through the frontend.
2. The dashboard sends infrastructure content to `POST /analyze`.
3. The backend chooses an AI provider from the selected model or `.env`.
4. AI analysis runs first; if unavailable, the Terraform/Kubernetes rule engine runs.
5. Oumi scoring is added to each issue.
6. The API returns a drift score, timeline, issues, provider, and model metadata.
7. If email is enabled and the user supplied an address, results are sent asynchronously.
8. For fixes, the frontend/backend can call AutoFix endpoints to generate or apply unified diffs.

## Project Structure

```text
infra-pilot/
├── backend/
│   ├── ai/                     # Gemini, Ollama, Oumi, Cline, and Oumi trainer clients
│   ├── routes/                 # Auth and AutoFix API routers
│   ├── services/
│   │   ├── analyzer.py         # Main analysis orchestration
│   │   ├── emailer.py          # Optional email notifications
│   │   └── rules/              # Terraform and Kubernetes rule fallback
│   ├── auth.py                 # JWT/password auth helpers
│   ├── database.py             # SQLAlchemy + SQLite setup
│   ├── main.py                 # FastAPI app
│   ├── models.py               # API request/response models
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/         # Analysis UI, issue cards, timeline, auth guard
│   │   ├── components/ui/      # Reusable UI and animated chat interface
│   │   ├── pages/              # Home, login/register, dashboard
│   │   ├── App.tsx             # Routes
│   │   └── types.ts
│   ├── package.json
│   └── vite.config.ts
├── cline/workflows/autofix.json
├── scripts/run_cline.sh
├── scripts/apply_patch.sh
├── DESIGN.md
└── PROJECT_LOG.md
```

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Ollama, if you want local model analysis
- Optional API keys for Gemini or Oumi
- Optional Cline/VS Code setup for AutoFix patch generation

## Backend Setup

```bash
cd infra-pilot/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On Windows PowerShell, activate the virtual environment with:

```powershell
venv\Scripts\Activate.ps1
```

The backend runs at `http://localhost:8000`.

Interactive API docs are available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

```bash
cd infra-pilot/frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` unless Vite selects another port. The current frontend calls the backend at `http://localhost:8000`.

## Environment Configuration

Copy `backend/.env.example` to `backend/.env` and adjust values as needed.

```bash
AI_PROVIDER=local
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT_SECONDS=360

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

OUMI_API_KEY=
CLINE_PATH=

EMAIL_ENABLED=false
EMAIL_FROM=your_gmail@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

Provider behavior:

- `AI_PROVIDER=local` uses Ollama through `http://localhost:11434`.
- `AI_PROVIDER=gemini` uses Gemini when `GEMINI_API_KEY` is configured.
- `AI_PROVIDER=oumi` uses Oumi when `OUMI_API_KEY` is configured.
- If the selected provider is unavailable, analysis falls back to the local rule engine.

## Local Ollama Models

Install Ollama, then pull any models you want to use from the dashboard:

```bash
ollama pull llama3:latest
ollama pull deepseek-r1:latest
ollama pull wizardlm2:7b
ollama pull qwen2.5:7b
```

Make sure Ollama is running before using local analysis:

```bash
ollama serve
```

## Authentication

The app includes simple email/password authentication backed by SQLite.

Available auth endpoints:

- `POST /auth/register`
- `POST /auth/token`
- `POST /auth/logout`
- `GET /auth/me`

The dashboard route is protected on the frontend. Users register or log in through `/login`; successful login stores a bearer token client-side.

## API Endpoints

### `GET /`

Health check.

### `POST /analyze`

Analyze Terraform or Kubernetes content.

```json
{
  "content": "resource \"aws_instance\" \"example\" {}",
  "file_type": "terraform",
  "model": "llama3:latest",
  "email": "optional@example.com"
}
```

Response shape:

```json
{
  "drift_score": 0.75,
  "timeline": [],
  "issues": [],
  "provider": "ollama",
  "model": "llama3:latest"
}
```

### `POST /autofix/generate`

Generate a unified diff patch for a detected issue.

```json
{
  "issue": {
    "title": "Public security group",
    "description": "Ingress allows 0.0.0.0/0",
    "fix_suggestion": "Restrict ingress CIDR ranges",
    "resource": "aws_security_group.web"
  },
  "file_content": "terraform content here",
  "file_path": "main.tf"
}
```

### `POST /autofix/apply`

Apply a generated patch to a workspace file.

```json
{
  "diff": "--- a/main.tf\n+++ b/main.tf\n...",
  "target_file": "main.tf",
  "workspace_path": "/path/to/workspace"
}
```

## Analysis Pipeline

1. The frontend sends infrastructure content, file type, selected model, and optional email to `/analyze`.
2. The backend chooses the provider from the requested model or `.env`.
3. The selected AI client attempts full-file analysis.
4. If AI analysis fails or returns no issues, the Terraform/Kubernetes rule engine runs.
5. Oumi scoring is added to each issue.
6. The backend returns drift score, timeline events, issue details, provider, and model metadata.
7. If email is enabled and an email address was provided, results are sent in the background.

## AutoFix / Cline Integration

InfraPilot includes an AutoFix path for infrastructure issues:

- `backend/ai/cline_agent.py` wraps the Cline workflow.
- `backend/routes/autofix.py` exposes patch generation and patch application endpoints.
- `cline/workflows/autofix.json` defines the workflow.
- `scripts/run_cline.sh` and `scripts/apply_patch.sh` provide shell automation.

AutoFix returns unified diff patches so generated changes can be reviewed before applying.

## Email Notifications

Email delivery is disabled by default and never blocks analysis responses. To enable it:

```bash
EMAIL_ENABLED=true
EMAIL_FROM=your_gmail@gmail.com
SMTP_USERNAME=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

For Gmail, use an App Password rather than your normal account password.

## Development Commands

Backend:

```bash
cd infra-pilot/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd infra-pilot/frontend
npm run dev
npm run build
```

Manual test flow:

1. Start the backend.
2. Start the frontend.
3. Open the frontend in the browser.
4. Register or log in.
5. Paste or attach a Terraform/Kubernetes file.
6. Select a model and file type.
7. Run analysis and review drift score, timeline, issues, and fix suggestions.

## Notes

- The default database is `backend/infrapilot.db`.
- The backend loads environment variables with `python-dotenv`.
- CORS is currently open for development.
- The current frontend uses hardcoded backend URLs pointing to `http://localhost:8000`.
- Rule-engine fallback keeps the app usable even when AI providers are not configured.

## License

Personal project by Adnan. Pull requests and enhancements are welcome.
