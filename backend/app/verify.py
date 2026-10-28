"""Fifteen transparent programmatic checks (not a VLM benchmark)."""
import math
from .models import CheckResult, Topic
from .physics import PhysicsResult


def run_checks(topic: Topic, problem: str, params: dict[str, float], result: PhysicsResult, code: str, scene_name: str) -> list[CheckResult]:
    def check(name: str, passed: bool, detail: str) -> CheckResult:
        return CheckResult(name=name, passed=bool(passed), detail=detail)

    values = list(result.values.values())
    checks = [
        check('Problem provided', bool(problem.strip()), 'A nonempty problem statement is present.'),
        check('Supported topic', topic in ('spring', 'projectile', 'incline', 'pendulum'), f'Topic: {topic}'),
        check('Parameters supplied', len(params) >= 2, f'{len(params)} physical parameters recorded.'),
        check('Finite inputs', all(math.isfinite(x) for x in params.values()), 'No NaN or infinity allowed.'),
        check('Positive physical quantities', all(v > 0 for k,v in params.items() if k != 'angle_deg'), 'Physical magnitudes must be positive.'),
        check('Valid angle domain', ('angle_deg' not in params) or 0 < params['angle_deg'] < 90, 'Angle is within model domain.'),
        check('Result available', bool(result.values), 'At least one computed output is present.'),
        check('Finite results', all(isinstance(v, (int,float)) and math.isfinite(v) for v in values), 'Numerical outputs are finite.'),
        check('Physical result domain', all(v >= 0 for v in values if isinstance(v,(int,float))), 'Output magnitudes are nonnegative.'),
        check('Explanatory steps', len(result.steps) >= 4, f'{len(result.steps)} explanation steps.'),
        check('Step equations', all(s.formula.strip() for s in result.steps), 'Each explanation step includes an equation.'),
        check('Manim scene defined', f'class {scene_name}(Scene):' in code, 'Named Manim Scene subclass found.'),
        check('Expected Manim import', code.startswith('from manim import *'), 'Template uses Manim Community.'),
        check('No external execution APIs', all(token not in code for token in ('subprocess', 'os.system', 'eval(', 'exec(', '__import__', 'open(')), 'Vetted templates exclude dangerous calls.'),
        check('Generated code length', 300 <= len(code) <= 16000, f'Code size: {len(code)} characters.'),
    ]
    return checks
