import pytest
from app import app
from random import randint

@pytest.fixture(scope='module')
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='module')
def get_token(client):
    email = f"test{randint(1, 999999)}@mail.com"
    user = {
        "email": email,
        "password": "testpassword12345!!##",
        "name": "Alex"
    }
    response = client.post('/register', json=user)
    assert response.status_code == 201, f"Registration failed: {response.get_json()}"

    token_response = client.post('/get_token', json=user)
    assert token_response.status_code == 200

    token_data = token_response.get_json()
    token = token_data['token']

    return token

def test_add_task(client, get_token):
    for i in range(5):
        headers = {"Authorization": f"Bearer {get_token}",
                   "Content-Type": "application/json",
                   "Accept": "application/json"}
        task = {
        "title": f"Task Nr/{i}",
        "deadline": "11/10/2027",
        "description": "Description 12233"
    }
        response = client.post('tasks/add_task', headers=headers, json=task)
        assert response.status_code == 201, f"Task failed: {response.get_json()}"

def test_get_tasks(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}",
               "Content-Type": "application/json",
               "Accept": "application/json"}
    response = client.get('tasks/get_tasks', headers=headers)
    assert response.status_code == 200