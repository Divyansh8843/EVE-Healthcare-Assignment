"""Tests for authentication endpoints."""
import pytest


class TestSignup:
    def test_signup_success(self, client):
        resp = client.post("/auth/signup", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "strongpass1",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert "id" in data
        assert "hashed_password" not in data  # sensitive field must not leak

    def test_signup_duplicate_email(self, client):
        payload = {"name": "Bob", "email": "bob@example.com", "password": "strongpass1"}
        client.post("/auth/signup", json=payload)
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_signup_invalid_email(self, client):
        resp = client.post("/auth/signup", json={
            "name": "Charlie",
            "email": "not-an-email",
            "password": "strongpass1",
        })
        assert resp.status_code == 422

    def test_signup_short_password(self, client):
        resp = client.post("/auth/signup", json={
            "name": "Diana",
            "email": "diana@example.com",
            "password": "abc",
        })
        assert resp.status_code == 422

    def test_signup_blank_name(self, client):
        resp = client.post("/auth/signup", json={
            "name": "  ",
            "email": "eve@example.com",
            "password": "strongpass1",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "securepass123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "anypassword",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client, registered_user):
        resp = client.get("/auth/me", headers=registered_user["headers"])
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_me_unauthenticated(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_token(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401
