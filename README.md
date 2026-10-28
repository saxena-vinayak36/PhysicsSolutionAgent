# PhysicsSolutionAgent ⚛️

**Solve. Visualize. Learn.** A working, open-source full-stack physics education starter built with **React + TypeScript**, **FastAPI + Python**, and optional **Manim Community** rendering.

## What works today

- Responsive dashboard for the supported physics examples.
- Four numerical solvers: **mass–spring**, **projectile motion**, **frictionless inclined plane**, and **small-angle pendulum**.
- Editable physical parameters and natural-language problem descriptions for context.
- Step-by-step calculations and a browser-based animated SVG model for each example.
- Downloadable **Manim `.py`** scenes generated from fixed, reviewed templates.
- Optional local MP4 rendering through installed Manim (off by default).
- A **15-check deterministic validation panel** for assumptions, values, outputs, and generated code.
- FastAPI docs (`/docs`), API tests, and a GitHub Actions CI workflow.

### Important scope notes

This is an original starter implementation. It does **not** autonomously solve arbitrary physics problems, run model-generated code, or perform a 15-stage vision-language-model (VLM) evaluation. The current 15 checks are deterministic programmatic checks, not a VLM benchmark. The app runs without API keys; an LLM/VLM integration is future work. Select a supported scenario and use its explicit parameter fields rather than relying on the problem text as a general-purpose parser.

The SVG preview is a teaching aid, not a scientifically exact frame-by-frame Manim render. Manim scenes are available as source; exporting an MP4 requires installing Manim and enabling rendering.

## Requirements

- Python **3.10+**
- Node.js **20+** and npm
- Optional: [Manim Community](https://docs.manim.community/en/stable/installation.html), including its OS-level graphics/LaTeX dependencies

## Start locally

Open **two terminals** from the repository root.

**Terminal 1 — backend**

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements-dev.txt
export PYTHONPATH=backend      # Windows PowerShell: $env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload --app-dir backend --port 8000
```

Check [http://localhost:8000/api/health](http://localhost:8000/api/health) and [http://localhost:8000/docs](http://localhost:8000/docs).

**Terminal 2 — frontend**

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` requests to port 8000.

### Test and build

```bash
# repo root, with venv active
PYTHONPATH=backend pytest -q backend/tests
cd frontend && npm run build
```

## Optional Manim video export

1. Install Manim Community and its dependencies following the official installation instructions; verify with `manim --version`.
2. With the backend virtual environment active, set `ENABLE_MANIM=true` (PowerShell: `$env:ENABLE_MANIM='true'`).
3. Restart the backend.
4. Generate a solution, then click **Render MP4**. Rendering uses allowlisted templates, allows at most two concurrent jobs, and has a 100-second timeout. Results are temporary and are not stored in a database.

Manual CLI rendering example after downloading a scene:

```bash
manim -ql spring_scene.py SpringScene
```

## API endpoints

| Endpoint | Description |
|---|---|
| `GET /api/health` | API and Manim capability flags |
| `GET /api/examples` | Four example problem fixtures |
| `POST /api/solve` | Validate parameters and return calculations, scene source, and 15 checks |
| `POST /api/render/{solution_id}` | Queue an optional Manim render |
| `GET /api/jobs/{job_id}` | Check render status |
| `GET /api/video/{job_id}` | Stream a finished MP4 |

Sample request:

```bash
curl -X POST http://127.0.0.1:8000/api/solve \
  -H 'Content-Type: application/json' \
  -d '{"topic":"spring","problem":"A 2 kg block is attached to a spring of constant 50 N/m.","parameters":{"mass":2,"k":50,"amplitude":0.2}}'
```

## Project structure

```text
PhysicsSolutionAgent/
  backend/
    app/
      animation.py       # reviewed Manim source templates
      main.py            # FastAPI + rendering jobs
      models.py          # request/response models
      physics.py         # numeric solvers and input validation
      verify.py          # 15 deterministic checks
    tests/test_api.py
    requirements.txt
    requirements-dev.txt
  frontend/
    src/
      components/PhysicsPreview.tsx
      App.tsx
      api.ts
      main.tsx
      styles.css
      types.ts
    index.html
    package.json
    tsconfig.json
    vite.config.ts
  .github/workflows/ci.yml
  .env.example
  .gitignore
  README.md
  LICENSE
```

## Security and engineering notes

- **Never execute model/user-authored Python.** Numeric parameters are interpolated into fixed scene templates.
- Only four topics are supported; invalid physical values produce clear 422 errors.
- CORS is restricted to local Vite development origins.
- Manim rendering is disabled by default. For public deployment, isolate rendering in an unprivileged container with network/filesystem restrictions and add authentication, rate limits, and persistence.
- Solution and render state are held in memory; restarting the API loses job references.

## Future work

- Add a gated LLM parser that emits constrained problem schemas and requests clarification when assumptions are missing.
- Implement an actual VLM evaluation pipeline with generated frames, model scoring, human validation, and tracked datasets.
- Add retrieval over physics references and unit consistency using a symbolic unit system.
- Use task queues and isolated containers before hosting the rendering service publicly.

## Author

Starter prepared for Vinayak Saxena. Repository: https://github.com/saxena-vinayak36/PhysicsSolutionAgent
