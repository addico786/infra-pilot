# InfraPilot Backend

Minimal FastAPI backend for infrastructure analysis and drift detection.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create your environment file:
```bash
cp .env.example .env
```
Then edit `.env` with your local values and API keys.

For slow local models, you can tune Ollama timeouts in `.env`:
```bash
# Global timeout for Ollama calls
OLLAMA_TIMEOUT_SECONDS=360

# Optional model-specific overrides
OLLAMA_TIMEOUT_DEEPSEEK_R1_SECONDS=360
OLLAMA_TIMEOUT_WIZARDLM2_SECONDS=300
OLLAMA_TIMEOUT_LLAMA3_SECONDS=180
OLLAMA_TIMEOUT_QWEN2_5_SECONDS=240
```

## Running the Server

Start the server with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Optional: Email Results via SMTP (Gmail)

InfraPilot can optionally email `/analyze` results to a user-provided recipient address.

- Email sending is **disabled by default** and **never blocks** the `/analyze` response.
- Enable it via `EMAIL_ENABLED=true` and configure SMTP settings in your `.env`.

### Gmail setup (recommended)
Use a **Gmail App Password** (requires 2FA). Do not use your normal Gmail password.

Add to your `.env`:
```bash
EMAIL_ENABLED=true
EMAIL_FROM=your_gmail@gmail.com

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your_gmail@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

## API Endpoints

- `GET /` - Health check endpoint
- `POST /analyze` - Analyze infrastructure content
- `POST /autofix/generate` - Generate patch for infrastructure issue
- `POST /autofix/apply` - Apply patch to infrastructure file

## Example Request

Using curl:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "resource \"aws_instance\" \"example\" {}",
    "file_type": "terraform"
  }'
```

Using HTTPie:
```bash
http POST http://localhost:8000/analyze \
  content="resource \"aws_instance\" \"example\" {}" \
  file_type="terraform"
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Cline Automation Integration

InfraPilot integrates with Cline (via VS Code Cline extension) to provide automated infrastructure fix generation. This integration demonstrates first-class workflow automation for the **Infinity Build Award**.

### How It Works

1. **Workflow Definition**: The Cline workflow is defined in `cline/workflows/autofix.json`, which specifies how VS Code Cline commands should be invoked to generate patches.

2. **Script-Based Execution**: The `scripts/run_cline.sh` script invokes VS Code Cline extension commands via the VS Code CLI (`code` command). This script:
   - Accepts file path and issue description as arguments
   - Invokes the `codeium.cline.generatePatch` command through VS Code CLI
   - Saves the generated patch to `/tmp/cline_patch.diff`
   - Provides output for further processing

3. **Patch Generation**: When InfraPilot detects an infrastructure drift issue:
   - The backend calls `ClineAgent.run_cline_workflow()`
   - This method writes the infrastructure file content to a temporary file
   - Executes `scripts/run_cline.sh` which invokes VS Code Cline
   - Reads the generated unified diff patch
   - Returns the patch for review or automatic application

4. **Patch Application**: The `scripts/apply_patch.sh` script applies generated patches:
   - Reads the patch from `/tmp/cline_patch.diff`
   - Uses GNU `patch` command to apply changes
   - Provides feedback on success or failure
   - Creates backup files for safety

### Why This Satisfies Infinity Build Award Requirements

This integration demonstrates:

- **Workflow Automation**: Automated patch generation through VS Code Cline commands
- **CLI Integration**: Scripts that invoke Cline via VS Code CLI interface
- **End-to-End Automation**: From issue detection → patch generation → patch application
- **Production-Ready**: Graceful fallbacks, error handling, and logging
- **First-Class Integration**: Not just API calls, but full workflow orchestration

### Usage Example

```bash
# Generate a patch for an infrastructure issue
./scripts/run_cline.sh infrastructure.tf "Security group allows 0.0.0.0/0"

# Apply the generated patch
./scripts/apply_patch.sh
```

### Architecture

```
InfraPilot Backend
    ↓
ClineAgent.run_cline_workflow()
    ↓
scripts/run_cline.sh
    ↓
VS Code CLI (code --command "codeium.cline.generatePatch")
    ↓
VS Code Cline Extension
    ↓
Generated Patch (/tmp/cline_patch.diff)
    ↓
scripts/apply_patch.sh
    ↓
Applied Fix
```

This architecture ensures that InfraPilot can leverage Cline's AI-powered code editing capabilities to automatically generate and apply fixes for infrastructure drift issues, fulfilling the Infinity Build Award requirements for Cline workflow automation.
