"""Deterministic, unit-tested solvers for four introductory mechanics scenarios.

This service intentionally does not execute user or LLM-supplied Python code.
It selects vetted Manim templates based on a small, documented topic allowlist.
"""
import math
import re
from dataclasses import dataclass
from typing import Any

from .models import Example, SolutionStep, Topic

G = 9.81  # m/s^2

EXAMPLES = [
    Example(topic='spring', title='Simple Harmonic Motion', problem=(
        'A 2 kg block is attached to a spring of constant 50 N/m on a frictionless surface. '
        'It is displaced by 0.2 m and released. Find the period and animate the oscillation.'),
        parameters={'mass': 2, 'k': 50, 'amplitude': 0.2}),
    Example(topic='projectile', title='Projectile Motion', problem=(
        'A ball is launched at 20 m/s at an angle of 45 degrees above the horizontal. '
        'Calculate its flight time, maximum height, and range, then visualize the trajectory.'),
        parameters={'speed': 20, 'angle_deg': 45}),
    Example(topic='incline', title='Inclined Plane', problem=(
        'A 5 kg block slides down a frictionless incline at 30 degrees to the horizontal. '
        'Determine its acceleration and the distance after 3 seconds from rest.'),
        parameters={'mass': 5, 'angle_deg': 30, 'time': 3}),
    Example(topic='pendulum', title='Simple Pendulum', problem=(
        'A simple pendulum of length 1.5 m is released from 12 degrees. '
        'Estimate its small-angle oscillation period and visualize its motion.'),
        parameters={'length': 1.5, 'angle_deg': 12}),
]

DEFAULTS: dict[Topic, dict[str, float]] = {
    e.topic: dict(e.parameters) for e in EXAMPLES
}


class UnsupportedProblem(ValueError):
    pass


def infer_topic(problem: str) -> Topic:
    p = problem.lower()
    hits: list[Topic] = []
    patterns = {
        'spring': ('spring', 'harmonic', 'oscillat', 'hooke'),
        'projectile': ('projectile', 'launch', 'trajectory', 'throw', 'ballistic'),
        'incline': ('incline', 'ramp', 'slope'),
        'pendulum': ('pendulum',),
    }
    for kind, terms in patterns.items():
        if any(t in p for t in terms):
            hits.append(kind)  # type: ignore[arg-type]
    if len(hits) != 1:
        raise UnsupportedProblem(
            'Select exactly one supported topic: spring, projectile, incline, or pendulum. '
            'General free-form physics problems are not supported in this starter.'
        )
    return hits[0]


def _extract(problem: str, topic: Topic) -> dict[str, float]:
    """Conservative convenience extraction; values can always be set explicitly in the UI.

    Never claim to have parsed arbitrary natural language. Unknown values use displayed defaults.
    """
    p = problem.lower()
    out: dict[str, float] = {}
    tests = {
        'mass': r'(?:mass(?: of)?|block of)\s*(?:=|is)?\s*([0-9]+(?:\.[0-9]+)?)\s*kg',
        'k': r'(?:constant|k)\s*(?:of|=|is)?\s*([0-9]+(?:\.[0-9]+)?)\s*n\s*/\s*m',
        'amplitude': r'(?:displaced by|amplitude(?: of| =| is)?)\s*([0-9]+(?:\.[0-9]+)?)\s*m\b',
        'speed': r'(?:at|speed(?: of| =| is)?|velocity(?: of| =| is)?)\s*([0-9]+(?:\.[0-9]+)?)\s*m\s*/\s*s',
        'angle_deg': r'(?:at an angle of|at|incline at|from)\s*([0-9]+(?:\.[0-9]+)?)\s*degrees',
        'length': r'(?:length(?: of| =| is)?)\s*([0-9]+(?:\.[0-9]+)?)\s*m\b',
        'time': r'(?:after|for)\s*([0-9]+(?:\.[0-9]+)?)\s*s(?:econds)?\b',
    }
    allowed = {
        'spring': ('mass', 'k', 'amplitude'),
        'projectile': ('speed', 'angle_deg'),
        'incline': ('mass', 'angle_deg', 'time'),
        'pendulum': ('length', 'angle_deg'),
    }[topic]
    for name in allowed:
        match = re.search(tests[name], p)
        if match:
            out[name] = float(match.group(1))
    return out


def parameters_for(topic: Topic, problem: str, overrides: dict[str, float]) -> dict[str, float]:
    params = dict(DEFAULTS[topic])
    params.update(_extract(problem, topic))
    unknown = set(overrides) - set(params)
    if unknown:
        raise ValueError(f'Unknown parameters for {topic}: {", ".join(sorted(unknown))}')
    params.update(overrides)
    if any(not math.isfinite(v) for v in params.values()):
        raise ValueError('All parameters must be finite numbers.')
    positive = ('mass', 'k', 'amplitude', 'speed', 'length', 'time')
    if any(params.get(k, 1) <= 0 for k in positive):
        raise ValueError('Mass, spring constant, amplitude, speed, length, and time must be positive.')
    if 'angle_deg' in params:
        a = params['angle_deg']
        if topic == 'pendulum' and not 0 < a <= 15:
            raise ValueError('Small-angle pendulum approximation requires 0 < angle ≤ 15 degrees.')
        if topic in ('projectile', 'incline') and not 0 < a < 90:
            raise ValueError('Angle must be between 0 and 90 degrees.')
    if any(abs(v) > 1_000_000 for v in params.values()):
        raise ValueError('Parameter magnitude is outside the supported range.')
    return params


@dataclass
class PhysicsResult:
    title: str
    summary: str
    values: dict[str, Any]
    steps: list[SolutionStep]


def calculate(topic: Topic, p: dict[str, float]) -> PhysicsResult:
    if topic == 'spring':
        m, k, a = p['mass'], p['k'], p['amplitude']
        w = math.sqrt(k / m)
        period = 2 * math.pi / w
        return PhysicsResult('Simple Harmonic Motion',
            f'Angular frequency = {w:.3f} rad/s; period = {period:.3f} s.',
            {'angular_frequency_rad_s': round(w, 5), 'period_s': round(period, 5), 'max_speed_m_s': round(a*w, 5)},
            [SolutionStep(title='Model the system', explanation='Hooke’s law describes the restoring force.', formula='F = -kx'),
             SolutionStep(title='Apply Newton’s second law', explanation='The acceleration is proportional to negative displacement.', formula='m x\u2033 + kx = 0'),
             SolutionStep(title='Solve the motion', explanation='For release from maximum displacement, x(t) = A cos(ωt).', formula=f'ω = √(k/m) = {w:.3f} rad/s'),
             SolutionStep(title='Find the period', explanation='One full oscillation corresponds to 2π radians.', formula=f'T = 2π√(m/k) = {period:.3f} s')])
    if topic == 'projectile':
        v, rad = p['speed'], math.radians(p['angle_deg'])
        tof = 2*v*math.sin(rad)/G
        height = (v*math.sin(rad))**2/(2*G)
        distance = v*v*math.sin(2*rad)/G
        return PhysicsResult('Projectile Motion',
            f'Flight time = {tof:.3f} s; range = {distance:.3f} m; peak height = {height:.3f} m.',
            {'flight_time_s': round(tof, 5), 'range_m': round(distance, 5), 'max_height_m': round(height, 5)},
            [SolutionStep(title='Resolve the launch velocity', explanation='Split initial velocity into horizontal and vertical components.', formula=f'vₓ = {v*math.cos(rad):.3f} m/s; vᵧ = {v*math.sin(rad):.3f} m/s'),
             SolutionStep(title='Calculate flight time', explanation='At the landing height, vertical displacement is zero.', formula=f'T = 2v sin(θ)/g = {tof:.3f} s'),
             SolutionStep(title='Calculate maximum height', explanation='Vertical velocity vanishes at the top.', formula=f'H = (v sin(θ))²/(2g) = {height:.3f} m'),
             SolutionStep(title='Calculate range', explanation='Horizontal velocity is constant without air drag.', formula=f'R = v² sin(2θ)/g = {distance:.3f} m')])
    if topic == 'incline':
        angle, t = math.radians(p['angle_deg']), p['time']
        acceleration = G*math.sin(angle)
        distance = .5*acceleration*t*t
        return PhysicsResult('Frictionless Inclined Plane',
            f'Acceleration = {acceleration:.3f} m/s²; distance after {t:g} s = {distance:.3f} m.',
            {'acceleration_m_s2': round(acceleration, 5), 'distance_m': round(distance, 5), 'final_speed_m_s': round(acceleration*t, 5)},
            [SolutionStep(title='Resolve the forces', explanation='Gravity has a component mg sin(θ) along the ramp.', formula='F∥ = mg sin(θ)'),
             SolutionStep(title='Apply Newton’s second law', explanation='Mass cancels on a frictionless incline.', formula=f'a = g sin(θ) = {acceleration:.3f} m/s²'),
             SolutionStep(title='Use kinematics', explanation='Starting from rest, displacement grows quadratically with time.', formula='s = ½at²'),
             SolutionStep(title='Find distance', explanation='Substitute the selected duration.', formula=f's = {distance:.3f} m')])
    if topic == 'pendulum':
        length = p['length']
        period = 2*math.pi*math.sqrt(length/G)
        omega = math.sqrt(G/length)
        return PhysicsResult('Simple Pendulum',
            f'Small-angle period = {period:.3f} s (assuming negligible damping).',
            {'period_s': round(period, 5), 'angular_frequency_rad_s': round(omega, 5)},
            [SolutionStep(title='Identify the restoring torque', explanation='Gravity produces a tangential restoring force.', formula='Fₜ = -mg sin(θ)'),
             SolutionStep(title='Apply the small-angle approximation', explanation='For angles up to 15°, sin(θ) ≈ θ in radians.', formula='θ\u2033 + (g/L)θ = 0'),
             SolutionStep(title='Find angular frequency', explanation='Match the standard harmonic oscillator equation.', formula=f'ω = √(g/L) = {omega:.3f} rad/s'),
             SolutionStep(title='Find the period', explanation='Use the angular frequency to find oscillation time.', formula=f'T = 2π√(L/g) = {period:.3f} s')])
    raise UnsupportedProblem('Unsupported topic.')
