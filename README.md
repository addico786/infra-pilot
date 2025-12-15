# InfraPilot — AI-Powered Infrastructure Drift Detection & AutoFix

<div align="center">

![InfraPilot](https://img.shields.io/badge/InfraPilot-AI%20Drift%20Detection-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)

**Intelligent infrastructure analysis powered by multiple AI providers with automatic fix generation**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Sponsor Integrations](#-sponsor-integrations)

</div>

---

## 🚀 Features

### AI-Powered Analysis
- **Multi-Provider Support**: Choose from Gemini (cloud), Oumi (cloud), or Ollama (local) models
- **Model Selection**: Support for WizardLM2, Llama3, Qwen2.5, DeepSeek R1, and Gemini Pro
- **Intelligent Detection**: AI-driven identification of misconfigurations, security risks, and drift patterns
- **Timeline Prediction**: AI-generated timeline of potential infrastructure drift progression

### Local LLM Support
- **Ollama Integration**: Run analysis completely offline using local models
- **Multiple Models**: Support for wizardlm2:7b, llama3:8b, qwen2.5:7b, deepseek-r1:8b
- **Privacy-First**: No data leaves your machine when using local models

### Oumi RL Scoring
- **Reinforcement Learning**: Advanced severity scoring using fine-tuned models
- **Context-Aware**: RL models learn from infrastructure patterns to provide accurate risk assessment
- **Adaptive**: Scoring improves over time with more usage

### AutoFix Capabilities
- **Cline CLI Integration**: Generate patches automatically using Cline workflows
- **Unified Diff Format**: Standard patch format for easy review and application
- **One-Click Fixes**: Apply generated patches directly from the UI

### Timeline Simulation
- **Progressive Drift Modeling**: Predict how issues will evolve over time
- **Severity Tracking**: Visualize severity progression across timeline events
- **AI-Enhanced**: Timeline events enriched with AI predictions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Model Select │  │  Analysis UI │  │  AutoFix UI  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┴────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Analyzer Service                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐   │   │
│  │  │ AI Analysis   │→ │ Rule Engine  │→ │ RL Score │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Gemini Client │  │ Oumi Client   │  │ Ollama Client│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AutoFix Service                         │   │
│  │  ┌──────────────┐  ┌──────────────┐                 │   │
│  │  │ Cline Agent  │→ │ Patch Gen    │                 │   │
│  │  └──────────────┘  └──────────────┘                 │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

### Component Flow

1. **User Input** → Frontend receives infrastructure code and model selection
2. **AI Analysis** → Backend routes to selected AI provider (Gemini/Oumi/Ollama)
3. **Issue Detection** → AI identifies misconfigurations and drift patterns
4. **RL Scoring** → Oumi RL provides severity scores for each issue
5. **Timeline Generation** → AI predicts progressive drift timeline
6. **AutoFix** → Cline generates patches for identified issues
7. **Response** → Frontend displays results with provider/model metadata

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Ollama** (optional, for local models) - [Install Ollama](https://ollama.ai)
- **API Keys** (optional, for cloud models):
  - `GEMINI_API_KEY` for Gemini
  - `OUMI_API_KEY` for Oumi

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
echo "AI_PROVIDER=ollama" > .env
echo "OLLAMA_MODEL=llama3" >> .env
# Or for cloud models:
# echo "AI_PROVIDER=gemini" > .env
# echo "GEMINI_API_KEY=your_key_here" >> .env

# Run backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Running Ollama Models

```bash
# Install Ollama (if not already installed)
# Visit https://ollama.ai for installation instructions

# Pull a model
ollama pull llama3
ollama pull wizardlm2:7b
ollama pull qwen2.5:7b
ollama pull deepseek-r1:8b

# Start Ollama server (usually runs automatically)
ollama serve
```

### Testing AutoFix

1. Analyze a Terraform or Kubernetes file
2. Click "AutoFix (Beta)" on any issue
3. Review the generated patch in the modal
4. Copy or apply the patch

---

## 🔧 Environment Variables

### Backend (.env)

```bash
# AI Provider Selection
AI_PROVIDER=ollama          # Options: ollama, gemini, oumi

# Ollama Configuration (for local models)
OLLAMA_MODEL=llama3        # Default model for Ollama

# Cloud API Keys (optional)
GEMINI_API_KEY=your_key_here
OUMI_API_KEY=your_key_here
```

### Frontend

No environment variables required. Backend URL is configured in `App.tsx` (default: `http://localhost:8000`).

---

## 📊 API Endpoints

### POST `/analyze`

Analyze infrastructure content for drift and issues.

**Request:**
```json
{
  "content": "terraform code here...",
  "file_type": "terraform",
  "model": "wizardlm2:7b"
}
```

**Response:**
```json
{
  "drift_score": 0.75,
  "timeline": [...],
  "issues": [...],
  "provider": "ollama",
  "model": "wizardlm2:7b"
}
```

### POST `/autofix/generate`

Generate a patch for an issue.

**Request:**
```json
{
  "issue": {...},
  "file_content": "...",
  "file_path": "main.tf"
}
```

**Response:**
```json
{
  "success": true,
  "diff": "--- a/main.tf\n+++ b/main.tf\n...",
  "message": "Patch generated successfully"
}
```

---

## 🏆 Sponsor Integrations

### Infinity Build Award — Cline CLI Integration

InfraPilot integrates **Cline CLI** for automated patch generation:

- **Workflow Automation**: Uses Cline workflows (`cline/workflows/autofix.json`) to generate fixes
- **CLI Integration**: Scripts in `scripts/run_cline.sh` demonstrate Cline command execution
- **Patch Generation**: Automatically generates unified diff patches for infrastructure issues
- **One-Click Application**: Patches can be applied directly from the UI

**Files:**
- `backend/ai/cline_agent.py` - Cline integration agent
- `backend/routes/autofix.py` - AutoFix API endpoints
- `cline/workflows/autofix.json` - Cline workflow definition
- `scripts/run_cline.sh` - Cline CLI automation script

### Iron Intelligence Award — Oumi RL Integration

InfraPilot uses **Oumi Reinforcement Learning** for intelligent issue scoring:

- **RL-Based Scoring**: Fine-tuned models provide context-aware severity assessment
- **Adaptive Learning**: Models improve with usage patterns
- **Local Models**: Supports Qwen 0.5B and Llama 3 8B for RL scoring
- **Severity Adjustment**: RL models can adjust severity based on context

**Files:**
- `backend/ai/oumi_trainer.py` - Oumi RL training and scoring
- `backend/services/analyzer.py` - Integration of RL scoring into analysis pipeline

### Local LLM Category — Ollama Integration

InfraPilot fully supports **local LLM inference** via Ollama:

- **Privacy-First**: Complete offline analysis capability
- **Multiple Models**: Support for wizardlm2:7b, llama3:8b, qwen2.5:7b, deepseek-r1:8b
- **No API Keys Required**: Works entirely locally
- **Model Selection UI**: Frontend dropdown for easy model selection

**Files:**
- `backend/ai/ollama_client.py` - Ollama API client
- `frontend/src/components/AnalyzeForm.tsx` - Model selector UI

---

## 📁 Project Structure

```
we_make_devs/
├── backend/
│   ├── ai/                    # AI client implementations
│   │   ├── gemini_client.py   # Google Gemini integration
│   │   ├── ollama_client.py   # Local Ollama integration
│   │   ├── oumi_client.py     # Oumi AI integration
│   │   ├── oumi_trainer.py    # Oumi RL scoring
│   │   └── cline_agent.py     # Cline CLI agent
│   ├── routes/
│   │   └── autofix.py         # AutoFix API endpoints
│   ├── services/
│   │   ├── analyzer.py        # Main analysis orchestrator
│   │   └── rules/             # Rule-based detection (fallback)
│   ├── models.py              # Pydantic models
│   ├── main.py                # FastAPI application
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── AnalyzeForm.tsx
│   │   │   ├── SummaryCard.tsx
│   │   │   ├── IssueCard.tsx
│   │   │   ├── PatchViewer.tsx
│   │   │   └── ...
│   │   ├── hooks/
│   │   │   └── useToast.ts    # Toast notification hook
│   │   ├── App.tsx            # Main app component
│   │   └── types.ts            # TypeScript types
│   └── package.json
├── cline/
│   └── workflows/
│       └── autofix.json       # Cline workflow definition
├── scripts/
│   ├── run_cline.sh           # Cline CLI script
│   └── apply_patch.sh         # Patch application script
└── docs/
    └── SUBMISSION.md           # Submission documentation
```

---

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest  # (if tests are added)
```

### Manual Testing

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Open `http://localhost:5173`
4. Paste Terraform/Kubernetes code
5. Select AI model
6. Click "Analyze"
7. Review results and test AutoFix

---

## 🛠️ Development

### Adding New AI Providers

1. Create client in `backend/ai/` (e.g., `new_provider_client.py`)
2. Implement `analyze_infrastructure()` method
3. Update `_get_provider_and_model()` in `analyzer.py`
4. Add model option to frontend `MODEL_OPTIONS`

### Extending Rule Engine

1. Add rules to `backend/services/rules/terraform_rules.py` or `k8s_rules.py`
2. Rules return dict with: `rule_id`, `title`, `description`, `severity`, `resource`, `raw_detected_data`

---

## 📝 License

This is a personal poject but iam open to pull requests and engancements. Developed by Adnan.

---

## Acknowledgments

- **Cline** - For CLI automation and patch generation
- **Oumi** - For RL-based scoring capabilities
- **Ollama** - For local LLM inference
- **Gemini** - For cloud-based AI analysis

---

<div align="center">

**Built with ❤️ by Adnan for infrastructure reliability**

[Report Bug](https://github.com/your-repo/issues) • [Request Feature](https://github.com/your-repo/issues)

</div>

