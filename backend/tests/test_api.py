from fastapi.testclient import TestClient
import time

from app.main import app

client = TestClient(app)
TIMESTAMP = str(int(time.time() * 1000))


def test_summary_endpoint():
    response = client.get('/api/summary')
    assert response.status_code == 200
    data = response.json()
    assert 'totalSpending' in data
    assert data['financialHealthScore'] > 0


def test_auth_register_and_login():
    register = client.post(
        '/api/auth/register',
        json={'name': 'Ava', 'email': f'ava-{TIMESTAMP}@example.com', 'password': 'TestPass123!'},
    )
    assert register.status_code == 200
    payload = register.json()
    assert payload['user']['email'] == f'ava-{TIMESTAMP}@example.com'
    assert 'token' in payload

    login = client.post(
        '/api/auth/login',
        json={'email': f'ava-{TIMESTAMP}@example.com', 'password': 'TestPass123!'},
    )
    assert login.status_code == 200
    assert 'token' in login.json()


def test_expense_creation():
    response = client.post(
        '/api/expenses',
        json={
            'title': 'Lunch',
            'category': 'Food',
            'amount': 250,
            'date': '2026-09-01',
            'source': 'manual',
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body['title'] == 'Lunch'
    assert body['amount'] == 250


def test_dashboard_endpoint():
    response = client.get('/api/dashboard')
    assert response.status_code == 200
    body = response.json()
    assert 'summary' in body
    assert 'budgets' in body
    assert 'insights' in body


def test_ai_assistant_endpoint():
    response = client.get('/api/assistant')
    assert response.status_code == 200
    body = response.json()
    assert 'advice' in body
    assert 'recommendations' in body
