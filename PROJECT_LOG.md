# InfraPilot — plain-English project log

This file lives **outside** the `frontend` and `backend` folders on purpose. It is a **simple history** of what changed, what broke, and how we fixed it. Update it whenever you add a feature or fix a bug.

**How to update:** Add a new dated section at the top under “Recent changes,” in everyday language. Link docs when helpful.

---

## Recent changes (newest first)

### 2026-04-14 — Added animated footer component

- **What:** Replaced the old static footer with a new animated wave footer.
- **Where:** `frontend/src/components/ui/animated-footer.tsx`, wired in `frontend/src/App.tsx`, with styling in `frontend/src/index.css`.
- **Extras:** Added a sample usage file at `frontend/src/components/ui/animated-footer-demo.tsx`.

### 2026-04-14 — Animated dotted background integrated in frontend

- **What:** Added a Three.js animated dotted surface as a live background in the React app.
- **Where:** `frontend/src/components/ui/dotted-surface.tsx`, mounted in `frontend/src/App.tsx`, with z-layer styling in `frontend/src/index.css`.
- **Support files:** Added `frontend/src/lib/utils.ts` (`cn` helper), `frontend/src/components/ui/demo.tsx`, and wrapped app with `ThemeProvider` in `frontend/src/main.tsx`.
- **Dependencies:** Installed `three` and `next-themes` in frontend.

### 2026-04-14 — Integrations section disclaimer (UI)

- **What:** Under **Integrations** on the dashboard, added a short note that the Cline / Kestra / CodeRabbit buttons only show **example** snippets and are **not** wired to live services.
- **Where:** `frontend/src/components/SponsorActions.tsx`

### 2026-04-14 — Email drift score matches the dashboard

- **What:** Analysis emails now show drift as a **percentage** (for example `52%`), like the web UI, not as a decimal like `0.52`.
- **Where:** Backend email builder and email subject line.

### 2026-04-14 — Gemini cloud models aligned with Google AI Studio

- **What:** Gemini model names were updated so they match what your API key actually lists (for example `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-pro-latest`). Older names like `gemini-1.5-flash` were returning “model not found” for your project.
- **Where:** Backend Gemini client, analyzer defaults, frontend model dropdown, and `.env.example`.
- **Tip:** You can list models your key supports with the Google Generative Language API “list models” endpoint (see Resources below).

### 2026-04-14 — Ollama: longer waits for slow local models

- **Problem:** Models like **DeepSeek R1** and **WizardLM2** sometimes need more than120 seconds to answer. The backend timed out, then used the **rule engine** fallback. That made drift scores look wrong compared to when **Llama 3** finished in time.
- **What we did:** Default Ollama request timeout was increased (to **360 seconds**). You can still override with environment variables if needed (see `backend/.env.example`).
- **Lesson:** If logs show `Request timeout` then `falling back to rule engine`, the cloud/local model did not finish in time—not necessarily “broken.”

### 2026-04-14 — Optional email of analysis results (SMTP / Gmail)

- **What:** Users can enter an **optional email** on the analyze form. If the backend is configured, it sends a **summary email** after `/analyze` (HTML + plain text). Sending runs in the **background** so a slow or failed email does not block the API response.
- **Safety:** Email is **off** unless you set `EMAIL_ENABLED=true`. No email is sent if the field is empty.
- **Gmail:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your normal password, and keep it only in `.env` (never commit real keys).

### 2026-04-14 — `.env.example` for backend

- **What:** A template file so new setups know which variables exist (AI provider, Ollama timeouts, Gemini, SMTP, etc.). Copy to `.env` and fill in real values.

### 2026-04-14 — Frontend tweaks

- **Footer:** Copyright year set to **2026** in the main app footer.
- **Models:** Dropdown updated over time: some models removed temporarily, **WizardLM** and **DeepSeek** (`deepseek-r1:latest`) adjusted to match what is installed in Ollama; **Gemini** options updated to the 2.5 / `pro-latest` style names.

### Earlier project (before this log file)

From the main [README](README.md), InfraPilot was built as:

- A **React** frontend and **FastAPI** backend for infrastructure **drift** analysis (Terraform and Kubernetes).
- Support for **multiple AI paths**: local **Ollama**, cloud **Gemini**, **Oumi** for extra scoring, plus a **rule-based fallback** if AI fails.
- **AutoFix** ideas tied to **Cline** workflows and scripts under `cline/` and `scripts/` (see that README for details).

There was **no separate “chat log” file** in the repo before this document; the bullets above come from work done in Cursor on this codebase plus runtime notes (timeouts, Gemini 404s, fallback behavior).

---

## Quick glossary (simple terms)

| Term | Meaning |
|------|--------|
| **Drift score** | A 0–1 number inside the API; the **dashboard shows it as a percent** (0–100%). |
| **Fallback / rule engine** | If the AI call fails or times out, the backend still returns an answer using pattern rules—scores may not match “full AI” runs. |
| **Ollama** | Runs models on your computer; model names must match `ollama list`. |
| **Gemini API key** | Usually **one key per Google Cloud / AI Studio project**, not one key per model. Which **models** work is listed by Google for that key. |

---

## Resources (official docs)

- **FastAPI:** https://fastapi.tiangolo.com/
- **Google Gemini API (generate content):** https://ai.google.dev/api/generate-content  
- **List models (REST):** https://ai.google.dev/api/rest/v1beta/models/list  
- **Ollama:** https://github.com/ollama/ollama  
- **Gmail App Passwords:** https://support.google.com/accounts/answer/185833  

---

## Maintainer note

When you ship something new, add a short bullet under **Recent changes** with:

1. **What** changed (one sentence).  
2. **Why** (optional, if it fixes a bug).  
3. **Where** (folder or env var name), if useful.

That keeps this file honest without needing git history.
