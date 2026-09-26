import os
from pathlib import Path

# Banco novo a cada execução: senão um teste de campo único (2º POST = 409) falha na 2ª rodada.
Path("test.db").unlink(missing_ok=True)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import Settings
from app.db.session import SessionLocal
from app.main import app
from app.models.vote import Vote


def test_health_and_tasks():
    with TestClient(app) as client:  # "with" roda o lifespan (cria as tabelas)
        assert client.get("/api/health").json() == {"status": "ok", "database": "ok"}
        created = client.post("/api/tasks", json={"title": "teste"})
        assert created.status_code == 201
        assert created.json()["title"] == "teste"
        assert any(t["title"] == "teste" for t in client.get("/api/tasks").json())
        assert client.post("/api/tasks", json={"title": ""}).status_code == 422


def test_supabase_url_uses_psycopg():
    url = Settings(DATABASE_URL="postgres://u:p@h:5432/db").DATABASE_URL
    assert url == "postgresql+psycopg://u:p@h:5432/db"


def test_update_and_delete_task():
    with TestClient(app) as client:
        task_id = client.post("/api/tasks", json={"title": "editar"}).json()["id"]

        updated = client.patch(f"/api/tasks/{task_id}", json={"done": True})
        assert updated.status_code == 200
        assert updated.json() == {"id": task_id, "title": "editar", "done": True}
        assert client.patch(f"/api/tasks/{task_id}", json={"title": ""}).status_code == 422

        assert client.delete(f"/api/tasks/{task_id}").status_code == 204
        assert client.delete(f"/api/tasks/{task_id}").status_code == 404
        assert client.patch(f"/api/tasks/{task_id}", json={"done": True}).status_code == 404


def test_poll_create_list_get():
    with TestClient(app) as client:
        created = client.post(
            "/api/polls", json={"question": " Best color? ", "options": ["Red", " Blue "]}
        )
        assert created.status_code == 201
        poll = created.json()
        assert poll["question"] == "Best color?"
        assert [o["text"] for o in poll["options"]] == ["Red", "Blue"]
        assert poll["created_at"]

        assert any(p["id"] == poll["id"] for p in client.get("/api/polls").json())
        assert client.get(f"/api/polls/{poll['id']}").json() == poll
        assert client.get("/api/polls/999999").status_code == 404


def test_poll_validation():
    with TestClient(app) as client:
        for body in [
            {"question": "", "options": ["a", "b"]},
            {"question": "Q", "options": ["only one"]},
            {"question": "Q", "options": ["a", "  "]},
            {"question": "Q", "options": ["Same", "same"]},
        ]:
            assert client.post("/api/polls", json=body).status_code == 422, body


def _vote_count(poll_id: int) -> int:
    with SessionLocal() as db:
        return db.scalar(select(func.count()).where(Vote.poll_id == poll_id))


def test_vote_once_per_poll():
    with TestClient(app) as client:
        poll = client.post("/api/polls", json={"question": "Q", "options": ["a", "b"]}).json()
        a, b = (o["id"] for o in poll["options"])
        url = f"/api/polls/{poll['id']}/votes"

        created = client.post(url, json={"option_id": a, "voter_id": "v1"})
        assert created.status_code == 201
        assert created.json()["option_id"] == a

        # Same voter again, even for another option: rejected by the unique constraint.
        again = client.post(url, json={"option_id": b, "voter_id": "v1"})
        assert again.status_code == 409
        assert again.json()["detail"] == "You have already voted on this poll"
        assert _vote_count(poll["id"]) == 1

        # Another voter on this poll, and the same voter on another poll, are fine.
        assert client.post(url, json={"option_id": b, "voter_id": "v2"}).status_code == 201
        other = client.post("/api/polls", json={"question": "Q2", "options": ["x", "y"]}).json()
        other_url = f"/api/polls/{other['id']}/votes"
        body = {"option_id": other["options"][0]["id"], "voter_id": "v1"}
        assert client.post(other_url, json=body).status_code == 201
        assert _vote_count(poll["id"]) == 2


def test_vote_errors():
    with TestClient(app) as client:
        poll = client.post("/api/polls", json={"question": "Q", "options": ["a", "b"]}).json()
        other = client.post("/api/polls", json={"question": "Q2", "options": ["x", "y"]}).json()
        option_id = poll["options"][0]["id"]
        url = f"/api/polls/{poll['id']}/votes"

        wrong = client.post(url, json={"option_id": other["options"][0]["id"], "voter_id": "v"})
        assert wrong.status_code == 422
        assert wrong.json()["detail"] == "Option does not belong to this poll"
        assert client.post(url, json={"option_id": 999999, "voter_id": "v"}).status_code == 404
        body = {"option_id": option_id, "voter_id": "v"}
        assert client.post("/api/polls/999999/votes", json=body).status_code == 404
        assert client.post(url, json={"option_id": option_id, "voter_id": " "}).status_code == 422
        assert _vote_count(poll["id"]) == 0
