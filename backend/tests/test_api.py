import math
from fastapi.testclient import TestClient
from app.main import app
from app.physics import EXAMPLES, calculate, parameters_for

client = TestClient(app)


def test_health_and_examples():
    assert client.get('/api/health').status_code == 200
    assert len(client.get('/api/examples').json()) == 4


def test_supported_scenarios():
    for example in EXAMPLES:
        r = client.post('/api/solve', json=example.model_dump())
        assert r.status_code == 200, (example.topic, r.json())
        item = r.json()
        assert len(item['steps']) == 4
        assert len(item['checks']) == 15
        assert all(c['passed'] for c in item['checks']), item['checks']
        assert f"class {item['scene_name']}(Scene)" in item['manim_code']


def test_numerical_physics():
    spring = calculate('spring', parameters_for('spring', 'A spring moves.', {'mass':2,'k':50,'amplitude':.2}))
    assert math.isclose(spring.values['period_s'], 2*math.pi/math.sqrt(25), abs_tol=1e-4)
    incline = calculate('incline', parameters_for('incline', 'Frictionless incline.', {'mass':5,'angle_deg':30,'time':3}))
    assert math.isclose(incline.values['acceleration_m_s2'], 4.905, abs_tol=1e-4)
    projectile = calculate('projectile', parameters_for('projectile', 'Projectile launched.', {'speed':20,'angle_deg':45}))
    assert 40 < projectile.values['range_m'] < 41


def test_rejects_unsafe_or_unsupported_inputs():
    assert client.post('/api/solve', json={'problem':'Do any advanced quantum theory you like.'}).status_code == 422
    assert client.post('/api/solve', json={'topic':'spring','problem':'An oscillating spring.', 'parameters':{'mass':-2}}).status_code == 422
    assert client.post('/api/solve', json={'topic':'spring','problem':'An oscillating spring.', 'parameters':{'python':'print(1)'}}).status_code == 422
    assert client.post('/api/solve', json={'topic':'pendulum','problem':'A swinging pendulum.', 'parameters':{'angle_deg':35}}).status_code == 422


def test_manim_off_by_default():
    result = client.post('/api/solve', json=EXAMPLES[0].model_dump()).json()
    r = client.post(f"/api/render/{result['id']}")
    assert r.status_code == 503
