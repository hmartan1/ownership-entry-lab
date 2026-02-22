# Ownership Entry Lab (MVP)
Minimal runnable prototype of the "Ownership Entry Lab" 8‑week companion.

## What this is
A lightweight Streamlit web app prototype that supports:
- Family workspace creation
- Participants: Founder + NextGen (2–3)
- Weekly modules (8 weeks) with prompts
- Individual answers (each user sees only their answers; admin sees all)
- Facilitator dashboard (admin)
- Exports: JSON + PDF "Ownership Readiness Map" draft
- Data stored locally in SQLite

## What this is NOT (yet)
- Production-grade authentication / tenant isolation
- Cloud hosting
- Real LLM integration (there is an optional hook)

## Run locally
1) Create a venv and install deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2) Start:
   ```bash
   streamlit run app.py
   ```
3) Open the URL shown in terminal.

## Default login model (prototype)
This MVP uses a simple "access code" per user (not secure; for prototype only).
- Create a family workspace as Admin.
- Then create users with role and access code.
- Users login with Family Code + Access Code.

## Optional LLM integration
If you want real AI summaries, you can extend `ai.py` with your provider.
The current `ai.py` generates a heuristic summary (keywords + themes).

## Data
SQLite DB is created at `data/app.db`.
Exports are saved to `exports/`.

