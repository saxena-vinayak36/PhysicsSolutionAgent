from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import threading
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .animation import make_manim
from .models import Example, RenderStatus, Solution, SolveRequest
from .physics import EXAMPLES, UnsupportedProblem, calculate, infer_topic, parameters_for
from .verify import run_checks

app = FastAPI(title='PhysicsSolutionAgent', version='0.1.0', description='Verifiable introductory physics solutions and Manim templates')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
                   allow_credentials=False, allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

SOLUTIONS: dict[str, Solution] = {}
JOBS: dict[str, RenderStatus] = {}
LOCK = threading.Lock()
MEDIA_DIR = Path(os.getenv('PHYSICS_MEDIA_DIR', Path(tempfile.gettempdir()) / 'physics-solution-agent-media'))
ENABLE_MANIM = os.getenv('ENABLE_MANIM', 'false').lower() == 'true'


@app.get('/api/health')
def health():
    return {'status': 'ok', 'manim_enabled': ENABLE_MANIM, 'manim_available': shutil.which('manim') is not None}


@app.get('/api/examples', response_model=list[Example])
def examples():
    return EXAMPLES


@app.post('/api/solve', response_model=Solution)
def solve(req: SolveRequest):
    try:
        topic = req.topic or infer_topic(req.problem)
        params = parameters_for(topic, req.problem, req.parameters)
        physics = calculate(topic, params)
        code, name = make_manim(topic, params)
        checks = run_checks(topic, req.problem, params, physics, code, name)
        solution = Solution(id=str(uuid.uuid4()), topic=topic, title=physics.title, summary=physics.summary,
                            problem=req.problem, parameters=params, result=physics.values, steps=physics.steps,
                            manim_code=code, scene_name=name, checks=checks)
        with LOCK:
            # Bounded in-memory cache; no sensitive inputs stored persistently.
            if len(SOLUTIONS) > 100:
                SOLUTIONS.pop(next(iter(SOLUTIONS)))
            SOLUTIONS[solution.id] = solution
        return solution
    except (ValueError, UnsupportedProblem) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _render(job_id: str, solution: Solution):
    with LOCK:
        JOBS[job_id] = RenderStatus(job_id=job_id, status='running', message='Rendering template with Manim...')
    work = MEDIA_DIR / job_id
    try:
        work.mkdir(parents=True, exist_ok=False)
        source = work / 'scene.py'
        source.write_text(solution.manim_code, encoding='utf-8')
        command = ['manim', '-ql', '--disable_caching', '--media_dir', str(work / 'media'),
                   '-o', 'animation.mp4', str(source), solution.scene_name]
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=100, cwd=work)
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout)[-1200:])
        matches = list((work / 'media').rglob('animation.mp4'))
        if not matches:
            raise RuntimeError('Manim succeeded but no MP4 was produced.')
        final = work / 'animation.mp4'
        shutil.copyfile(matches[0], final)
        with LOCK:
            JOBS[job_id] = RenderStatus(job_id=job_id, status='complete', video_url=f'/api/video/{job_id}', message='Render complete.')
    except Exception as exc:
        with LOCK:
            JOBS[job_id] = RenderStatus(job_id=job_id, status='failed', message=str(exc)[:700])


@app.post('/api/render/{solution_id}', response_model=RenderStatus)
def render(solution_id: str, background_tasks: BackgroundTasks):
    if not ENABLE_MANIM:
        raise HTTPException(status_code=503, detail='Video rendering is disabled. Install Manim and set ENABLE_MANIM=true.')
    if not shutil.which('manim'):
        raise HTTPException(status_code=503, detail='Manim executable not found on PATH.')
    with LOCK:
        solution = SOLUTIONS.get(solution_id)
        active = sum(j.status in ('queued','running') for j in JOBS.values())
    if not solution:
        raise HTTPException(status_code=404, detail='Solution expired. Generate it again.')
    if active >= 2:
        raise HTTPException(status_code=429, detail='Rendering queue is full. Try again later.')
    job_id = str(uuid.uuid4())
    with LOCK:
        JOBS[job_id] = RenderStatus(job_id=job_id, status='queued', message='Waiting for render worker.')
    background_tasks.add_task(_render, job_id, solution)
    return JOBS[job_id]


@app.get('/api/jobs/{job_id}', response_model=RenderStatus)
def job_status(job_id: str):
    with LOCK:
        current = JOBS.get(job_id)
    if not current:
        raise HTTPException(status_code=404, detail='Unknown render job.')
    return current


@app.get('/api/video/{job_id}')
def video(job_id: str):
    with LOCK:
        job = JOBS.get(job_id)
    path = MEDIA_DIR / job_id / 'animation.mp4'
    if not job or job.status != 'complete' or not path.is_file():
        raise HTTPException(status_code=404, detail='Video not available.')
    return FileResponse(path, media_type='video/mp4', filename=f'physics-{job_id}.mp4')
