# Deploy on Leapcell (no Docker)

Leapcell **clones the whole Git repo** and runs your Build Command. It does not use a custom Dockerfile, so you cannot exclude files via `.dockerignore`.

## How to keep deploy lean

1. **Rely on `.gitignore`**  
   Anything in `.gitignore` is not committed, so it is **not in the repo** and Leapcell will not clone it (e.g. `venv/`, `__pycache__/`, `.env`, `.pytest_cache/`).  
   → Only commit what you need for production; the rest is already “ignored” for deploy.

2. **Faster install**  
   In Leapcell **Build Command** use:
   ```bash
   pip install -r requirements-prod.txt
   ```
   so dev/test deps (e.g. pytest) are not installed and build is quicker.

3. **Start command**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
   (Port according to Leapcell’s required port, often 8080.)

4. **No deploy-time ignore file**  
   Without Docker, there is no “ignore at deploy” step. The only way to exclude something is to **not commit it** (keep it in `.gitignore`). If you need to exclude already-committed folders later, you’d have to remove them from the repo and add them to `.gitignore` (history rewrite if needed).
