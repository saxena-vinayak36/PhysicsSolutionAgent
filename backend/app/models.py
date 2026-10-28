from typing import Literal
from pydantic import BaseModel, Field

Topic = Literal['spring', 'projectile', 'incline', 'pendulum']


class SolveRequest(BaseModel):
    problem: str = Field(min_length=8, max_length=3000)
    topic: Topic | None = None
    parameters: dict[str, float] = Field(default_factory=dict)


class SolutionStep(BaseModel):
    title: str
    explanation: str
    formula: str = ''


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str


class Solution(BaseModel):
    id: str
    topic: Topic
    title: str
    summary: str
    problem: str
    parameters: dict[str, float]
    result: dict[str, float | str]
    steps: list[SolutionStep]
    manim_code: str
    scene_name: str
    checks: list[CheckResult]
    validation_note: str = '15 deterministic checks; not a vision-language-model evaluation.'


class RenderStatus(BaseModel):
    job_id: str
    status: Literal['queued', 'running', 'complete', 'failed']
    message: str = ''
    video_url: str | None = None


class Example(BaseModel):
    topic: Topic
    title: str
    problem: str
    parameters: dict[str, float]
