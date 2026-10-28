"""PhysicsSolutionAgent: deterministic, auditable classical-mechanics solver.

The supported scenarios are deliberately bounded. We do not execute arbitrary
Python emitted by a language model.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

G = 9.81
MAX_PROBLEM_LENGTH = 4000

EXAMPLES = [
    {"id": "spring", "title": "Simple Harmonic Motion", "subtitle": "Mass and spring", "tag": "Oscillations", "problem": "A 2 kg block is attached to a spring with spring constant 8 N/m on a frictionless horizontal surface. It is displaced by 0.8 m and released. Find the period and show the oscillation."},
    {"id": "projectile", "title": "Projectile Motion", "subtitle": "Trajectory and range", "tag": "Kinematics", "problem": "A projectile is launched at 20 m/s at an angle of 45 degrees above the horizontal. Find its time of flight, range and maximum height. Visualize the trajectory."},
    {"id": "incline", "title": "Inclined Plane", "subtitle": "Forces and acceleration", "tag": "Newton's laws", "problem": "A 2 kg block slides from rest down a frictionless inclined plane at an angle of 30 degrees. Find its acceleration and show its motion over 5 meters."},
    {"id": "pendulum", "title": "Simple Pendulum", "subtitle": "Small-angle oscillations", "tag": "Oscillations", "problem": "A pendulum has length 1.5 m and is released from a small angle of 15 degrees. Find its approximate period and visualize its motion."},
]

class UnsupportedProblem(ValueError):
    """The problem cannot be safely solved by a supported model."""


def _number(pattern: str, text: str, default: float) -> float:
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1)) if match else default


def _scene(text: str) -> str:
    q = text.lower()
    if any(s in q for s in ("spring", "harmonic", "oscillator")):
        return "spring"
    if any(s in q for s in ("projectile", "launched", "thrown", "trajectory")):
        return "projectile"
    if any(s in q for s in ("incline", "inclined", "slope", "ramp")):
        return "incline"
    if any(s in q for s in ("pendulum", "swing", "bob")):
        return "pendulum"
    raise UnsupportedProblem("This starter supports spring motion, projectile motion, frictionless inclined planes, and simple pendulums. Try one of the example problems.")


def _positive(name: str, value: float, maximum: float = 100000) -> float:
    if not math.isfinite(value) or not 0 < value <= maximum:
        raise ValueError(f"{name} must be a positive finite value (up to {maximum:g}).")
    return value


def _steps(items):
    return [{"title": title, "detail": detail, "equation": equation} for title, detail, equation in items]


def solve(problem: str) -> dict:
    if not isinstance(problem, str) or not problem.strip():
        raise ValueError("Please enter a physics problem.")
    if len(problem) > MAX_PROBLEM_LENGTH:
        raise ValueError("Problem is too long (maximum 4,000 characters).")
    scene = _scene(problem)
    if scene == "spring":
        m = _positive("Mass", _number(r"(?:mass(?:\s+of)?|block\s+of)\s*(?:=|:)?\s*(\d+(?:\.\d+)?)\s*kg", problem, 2))
        k = _positive("Spring constant", _number(r"(?:spring\s+constant|constant\s+k|k\s*=)\s*(?:=|:|of)?\s*(\d+(?:\.\d+)?)\s*(?:n\s*/\s*m)?", problem, 8))
        a = _positive("Amplitude", _number(r"(?:displaced\s+by|amplitude(?:\s+of)?|distance\s+of)\s*(\d+(?:\.\d+)?)\s*m\b", problem, 0.8), 100)
        w = math.sqrt(k/m); period = 2*math.pi/w
        duration = 2 * period
        params = {"mass_kg":m, "spring_constant_n_per_m":k, "amplitude_m":a,"omega_rad_s":w}
        metrics = [{"label":"Period", "value":f"{period:.2f} s"}, {"label":"Frequency", "value":f"{1/period:.3f} Hz"}, {"label":"Angular frequency", "value":f"{w:.2f} rad/s"}]
        steps = _steps([
            ("Model the system", "A mass attached to an ideal spring on a frictionless surface experiences a restoring force.", "F = -kx"),
            ("Apply Newton's second law", "Substitute the restoring force into F = ma.", "m x'' + kx = 0"),
            ("Solve the oscillator", "For release from rest at maximum displacement, the phase is zero.", "x(t) = A cos(sqrt(k/m) t)"),
            ("Compute the time period", "The angular frequency is sqrt(k/m); its inverse sets the oscillation period.", f"T = 2*pi*sqrt(m/k) = {period:.3f} s")])
        def point(t):
            x=a*math.cos(w*t); v=-a*w*math.sin(w*t)
            return {"t":t,"x":x,"y":0,"vx":v,"energy":0.5*k*a*a}
        formula="T = 2*pi*sqrt(m/k)"
    elif scene == "projectile":
        speed = _positive("Launch speed", _number(r"(?:at|speed\s+of|velocity\s+of)\s*(\d+(?:\.\d+)?)\s*m\s*/\s*s", problem, 20), 1000)
        theta = _positive("Launch angle", _number(r"(?:angle\s+of|at\s+an\s+angle\s+of|at\s+an\s+angle)\s*(\d+(?:\.\d+)?)\s*(?:degrees|degree|deg|°)", problem,45), 89.9)
        radians=math.radians(theta); vx=speed*math.cos(radians); vy=speed*math.sin(radians)
        flight=2*vy/G; range_=vx*flight; height=vy*vy/(2*G); duration=flight
        params={"speed_m_s":speed, "angle_deg":theta, "gravity_m_s2":G,"flight_s":flight,"range_m":range_,"height_m":height}
        metrics=[{"label":"Flight time","value":f"{flight:.2f} s"},{"label":"Range","value":f"{range_:.2f} m"},{"label":"Maximum height","value":f"{height:.2f} m"}]
        steps=_steps([
            ("Resolve velocity", "Split launch velocity into horizontal and vertical components.","v_x = v0 cos(theta), v_y = v0 sin(theta)"),
            ("Write motion equations", "Neglect air resistance and take the launch point as y = 0.","x = v_x t, y = v_y t - 0.5 g t^2"),
            ("Find time of flight", "Set the final vertical displacement to zero (landing at launch height).",f"T = 2 v_y/g = {flight:.3f} s"),
            ("Find range and height", "Use horizontal displacement at landing and vertical velocity zero at the peak.",f"R = {range_:.3f} m, H = {height:.3f} m")])
        def point(t):
            return {"t":t,"x":vx*t,"y":max(0,vy*t-0.5*G*t*t),"vx":vx,"energy":0.5*speed*speed}
        formula="R = v0^2 sin(2 theta)/g"
    elif scene == "incline":
        mass=_positive("Mass",_number(r"(?:mass(?:\s+of)?|block\s+of)\s*(\d+(?:\.\d+)?)\s*kg",problem,2))
        theta=_positive("Incline angle",_number(r"(?:angle\s+of|incline(?:d)?\s+(?:at\s+an\s+angle\s+of)?)\s*(\d+(?:\.\d+)?)\s*(?:degrees|degree|deg|°)",problem,30),89.9)
        distance=_positive("Travel distance",_number(r"(?:over|through|distance\s+of)\s*(\d+(?:\.\d+)?)\s*(?:m|meters)\b",problem,5),10000)
        accel=G*math.sin(math.radians(theta));duration=math.sqrt(2*distance/accel)
        params={"mass_kg":mass,"angle_deg":theta,"distance_m":distance,"acceleration_m_s2":accel}
        metrics=[{"label":"Acceleration","value":f"{accel:.2f} m/s²"},{"label":"Slide time","value":f"{duration:.2f} s"},{"label":"Final speed","value":f"{accel*duration:.2f} m/s"}]
        steps=_steps([
            ("Draw the free-body diagram", "Gravity acts vertically; resolve the force parallel to the slope.","F_parallel = mg sin(theta)"),
            ("Apply Newton's law", "There is no friction in this idealized problem.","a = g sin(theta)"),
            ("Find displacement", "The block is released from rest.","s = 0.5 a t^2"),
            ("Calculate travel time", "Solve for time after covering the given distance.",f"t = sqrt(2s/a) = {duration:.3f} s")])
        def point(t):
            s=.5*accel*t*t
            return {"t":t,"x":s,"y":-s*math.sin(math.radians(theta)),"vx":accel*t,"energy":0.5*(accel*t)**2+G*(distance-s)*math.sin(math.radians(theta))}
        formula="a = g sin(theta)"
    else:
        length=_positive("Pendulum length",_number(r"(?:length(?:\s+of)?|pendulum\s+of)\s*(\d+(?:\.\d+)?)\s*m\b",problem,1.5))
        theta=_positive("Initial angle",_number(r"(?:angle\s+of|from\s+(?:an?\s+)?(?:angle\s+of)?)\s*(\d+(?:\.\d+)?)\s*(?:degrees|degree|deg|°)",problem,15),45)
        w=math.sqrt(G/length);period=2*math.pi/w;duration=2*period
        params={"length_m":length,"initial_angle_deg":theta,"gravity_m_s2":G,"omega_rad_s":w}
        metrics=[{"label":"Period (approx.)","value":f"{period:.2f} s"},{"label":"Frequency","value":f"{1/period:.3f} Hz"},{"label":"Initial angle","value":f"{theta:g}°"}]
        steps=_steps([
            ("Define the forces", "The tangential component of gravity provides a restoring torque.","tau = -mgL sin(theta)"),
            ("Use the small-angle model", "For small angular displacements, sin(theta) is approximately theta.","theta'' + (g/L)theta = 0"),
            ("Solve the angular motion", "Release from rest at the initial angular displacement.","theta(t) = theta_0 cos(sqrt(g/L) t)"),
            ("Calculate the period", "The linearized pendulum has angular frequency sqrt(g/L).",f"T = 2*pi*sqrt(L/g) = {period:.3f} s")])
        theta0=math.radians(theta)
        def point(t):
            ang=theta0*math.cos(w*t)
            x=length*math.sin(ang); y=-length*math.cos(ang)
            return {"t":t,"x":x,"y":y,"theta":ang,"energy":0.5*(length*theta0*w*math.sin(w*t))**2 + G*length*(1-math.cos(ang))}
        formula="T = 2*pi*sqrt(L/g)  (small angle)"
    trajectory=[point(duration*i/120) for i in range(121)]
    return {"scene":scene,"title":next(e["title"] for e in EXAMPLES if e["id"]==scene),"problem":problem,"assumptions":assumptions(scene),"params":params,"metrics":metrics,"steps":steps,"formula":formula,"duration_s":duration,"trajectory":trajectory}


def assumptions(scene: str) -> list[str]:
    return {"spring":["Ideal spring; no friction", "Released from rest at maximum displacement"],
            "projectile":["No air resistance", "Launch and landing at equal height", "g = 9.81 m/s²"],
            "incline":["Frictionless plane", "Released from rest", "g = 9.81 m/s²"],
            "pendulum":["Small-angle approximation", "No damping", "Released from rest"]}[scene]
