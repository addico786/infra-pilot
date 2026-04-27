# InfraPilot — plain-English project log

This file lives **outside** the `frontend` and `backend` folders on purpose. It is a **simple history** of what changed, what broke, and how we fixed it. Update it whenever you add a feature or fix a bug.

**How to update:** Add a new dated section at the top under “Recent changes,” in everyday language. Link docs when helpful.

---

## Recent changes (newest first)

### 2026-04-27 — Added authentication system with JWT and SQLite

- **What:** Built a full auth system: users can register and log in. Backend uses SQLite with SQLAlchemy, bcrypt password hashing, and JWT access tokens. Frontend has a new `/login` page with an image-slider design (left panel shows rotating tech images, right panel has the form). After logging in, the token is stored in `localStorage` and the user is redirected to `/dashboard`.
- **Where:**
  - Backend: `backend/database.py` (SQLAlchemy User model + init), `backend/auth.py` (bcrypt + JWT), `backend/routes/auth.py` (register, login, logout, me endpoints).
  - Frontend: `frontend/src/pages/LoginPage.tsx`, `frontend/src/components/ui/image-slider.tsx`, `frontend/src/components/ui/input.tsx`, `frontend/src/components/ui/label.tsx`.
  - Updated `backend/main.py` to include the auth router, `frontend/src/App.tsx` to add the `/login` route, and `frontend/src/components/Navbar.tsx` to link "Get Started" to `/login`.

### 2026-04-25 — Removed AutoFix (Beta) button from frontend

- **What:** Removed the "AutoFix (Beta)" button from `IssueCard` and cleaned up all related unused code (`handleAutofix`, `handleApplyPatch`, `PatchViewer` modal, `fileContent` state) from `DashboardPage`.
- **Where:** `frontend/src/components/IssueCard.tsx`, `frontend/src/pages/DashboardPage.tsx`.

### 2026-04-25 — Trimmed Gemini options from model dropdown

- **What:** Removed "Gemini 2.5 Pro (Cloud)" and "Gemini Pro Latest (Cloud)" from the AI model selector in the dashboard, leaving only "Gemini 2.5 Flash (Cloud)" as the cloud option alongside the local models.
- **Where:** `frontend/src/components/AnalyzeForm.tsx` (`MODEL_OPTIONS` array).

### 2026-04-25 — Replaced hero with shadcn/ui-style animated hero

- **What:** Swapped out the old `ContainerScroll` hero + separate `Navbar` for a fully integrated `HeroSection` with sticky header, mobile hamburger menu, email CTA, dashboard mockup, and infinite logo slider.
- **New components:**
  - `frontend/src/components/blocks/hero-section-3.tsx` — main hero with `HeroHeader` (responsive nav), animated headline via `AnimatedGroup`, email capture form with `Button`, `LogoCloud` with `InfiniteSlider` + `ProgressiveBlur`, and dashboard-style `AppComponent` mockup.
  - `frontend/src/components/ui/button.tsx` — shadcn `Button` with `cva` variants.
  - `frontend/src/components/ui/animated-group.tsx` — `framer-motion` stagger animation wrapper.
  - `frontend/src/components/ui/infinite-slider.tsx` — auto-scrolling carousel with hover slowdown.
  - `frontend/src/components/ui/progressive-blur.tsx` — directional gradient blur mask.
- **Dependencies installed:** `@radix-ui/react-slot`, `class-variance-authority`, `react-use-measure`.
- **Adaptations made for React SPA (not Next.js):**
  - Replaced `next/link` with `react-router-dom` `Link`.
  - Replaced `href` props with `to` props.
  - Changed menu anchor links to match homepage section IDs (`#features`, `#how-it-works`, `#pricing`).
  - Replaced generic logo SVG with simple "InfraPilot" text logo.
  - Updated `AppComponent` mock text to infrastructure metrics (uptime, issues fixed).
- **Where:** Updated `frontend/src/pages/HomePage.tsx` to import `HeroSection` from `@/components/blocks/hero-section-3` and removed the old `Navbar` + `ContainerScroll` hero block.

### 2026-04-25 — Fixed missing Tailwind CSS configuration

- **Problem:** Homepage rendered completely unstyled — navbar links squished together, no card borders/shadows, hero padding broken, icons raw outlines. Root cause was Tailwind installed but unconfigured.
- **What was missing:** No `tailwind.config.js`, no `postcss.config.js`, and no `@tailwind` directives in `index.css`.
- **Fix:** Created `frontend/tailwind.config.js` (content paths for `src/**/*.{js,ts,jsx,tsx}`), `frontend/postcss.config.js` (wires Tailwind + autoprefixer), and added `@tailwind base; @tailwind components; @tailwind utilities;` to `frontend/src/index.css`.
- **Verification:** `npm run build` passes cleanly.

### 2026-04-25 — Marketing homepage + SPA routing

- **What:** Added a marketing homepage with hero scroll animation, extracted the AI dashboard to its own route, and wired everything with `react-router-dom`.
- **Why:** The app previously opened straight into the analyzer. Now users land on a marketing page (`/`) and navigate to the dashboard (`/dashboard`). This prepares the ground for adding auth (login/signup) next.
- **Where:**
  - `frontend/src/App.tsx` — rewritten as a `BrowserRouter` shell with two routes (`/` and `/dashboard`).
  - `frontend/src/pages/HomePage.tsx` — new marketing page with hero scroll animation (powered by `framer-motion`), features grid, "How it works" section, and pricing teaser. Uses the existing `AnimatedFooter`.
  - `frontend/src/pages/DashboardPage.tsx` — extracted the old `App.tsx` analyzer UI into a dedicated page.
  - `frontend/src/components/Navbar.tsx` — new sticky Apple-style navbar with "Features", "About", "Pricing", and a "Get Started" CTA linking to `/dashboard`. Mobile hamburger menu included.
  - `frontend/src/components/ui/container-scroll-animation.tsx` — new scroll-driven 3D card animation component (from the Aceternity-style template), typed for TypeScript.
  - `frontend/vite.config.ts` and `frontend/tsconfig.json` — added `@/*` path alias so imports like `@/components/ui/...` resolve correctly (shadcn convention).
- **Dependencies:** Installed `react-router-dom` in the frontend.
- **Design notes:** Homepage follows the Apple-inspired palette from `DESIGN.md` (`#f5f5f7`, `#0071e3`, `#1d1d1f`, `#6e6e73`, rounded cards, clean typography). Footer reuses the animated wave component already in the codebase.
- **Cleanup:** Removed the unused `loadingPatch` state variable and its setter to silence a TypeScript warning.

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
