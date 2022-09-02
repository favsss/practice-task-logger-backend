from email import header
import json
from fastapi.testclient import TestClient
from app.main import app


def check_user(client, user_id, username, email):
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200 
    data = response.json()
    assert data["user_name"] == username
    assert data["email"] == email

def check_project(client, project_id, project_name):
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200 
    data = response.json()
    assert data["name"] == project_name

def get_token(client):
    username = "dummy_user"
    password = "dummypassword1234"
    response = client.post("/token", data={
        "username": username,
        "password": password
    })

    data = response.json()
    return data["access_token"]

def test_smoke_test():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == { "message" : "Hello World"}

def test_get_users(client):
    response = client.get("/users")

    # database is initiated with a default row
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_create_user(client):
    response = client.post("/users", json={
        "user_name" : "dummy_user2",
        "email" : "dummy_email2@gmail.com",
        "password" : "dummypassword12342"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "dummy_email2@gmail.com"
    assert "id" in data 
    user_id = data["id"]

    check_user(client, user_id, "dummy_user2", "dummy_email2@gmail.com")


def test_update_user(client):
    user_id = 1
    updated_user_name = "dummy_user2"
    updated_email = "dummy_email2@gmail.com"
    response = client.patch(f"/users/{user_id}", json={
        "user_name" : updated_user_name,
        "email" : updated_email
    })

    assert response.status_code == 200
    data = response.json()
    assert data["user_name"] == updated_user_name
    assert data["email"] == updated_email

    check_user(client, user_id, updated_user_name, updated_email)

def test_delete_user(client):
    user_id = 1
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200 
    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_projects(client):
    response = client.get("/projects")

    assert response.status_code == 200
    assert len(response.json()) == 1

def test_create_project(client):
    project_name = "Dummy Project 2"
    response = client.post("/projects", json={
        "name" : project_name
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == project_name
    project_id = data["id"]

    check_project(client, project_id, project_name)

def test_update_project(client): 
    project_id = 1
    updated_project_name = "Dummy Project Updated"
    response = client.patch(f"/projects/{project_id}", json={
        "name" : updated_project_name
    })

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_project_name

    check_project(client, project_id, updated_project_name)

def test_delete_project(client):
    project_id = 1 
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    response = client.get("/projects")
    assert response.status_code == 200 
    assert len(response.json()) == 0

# def test_get_tasks(client):
#     token = get_token(client)

#     response = client.get("/tasks", headers={
#         "Authorization" : f"Bearer {token}"
#     })

#     assert response.status_code == 200 
#     assert len(response.json()) == 1

# def create_task(client):
    user_id = 1
    project_id = 1
    start_time = "1500"
    end_time = "1600"
    task_date = "2022-09-02"
    duration = 1
    description = "create task test"

    token = get_token(client)

    response = client.post("/tasks", json={
        "project_id" : project_id,
        "start_time" : start_time,
        "end_time" : end_time,
        "task_date" : task_date,
        "duration" : duration,
        "description" : description
    }, headers={
        "Authorization" : f"Bearer {token}"
    })

    print(response.json())

    assert response.status_code == 200 
    data = response.json()
    assert data["project_id"] == project_id
    assert data["duration"] == duration
    assert data["description"] == description
    assert data["user_id"] == user_id




