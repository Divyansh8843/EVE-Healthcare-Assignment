"""Tests for booking endpoints."""
import pytest
from datetime import datetime, timezone, timedelta


def future_time(hours: int = 24) -> str:
    dt = datetime.now(timezone.utc) + timedelta(hours=hours)
    return dt.isoformat()


def past_time() -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=1)
    return dt.isoformat()


class TestCreateBooking:
    def test_create_booking_success(self, client, registered_user, centre_and_test):
        resp = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"])
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "PENDING"
        assert float(data["amount"]) == 750.0

    def test_create_booking_unauthenticated(self, client, centre_and_test):
        resp = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        })
        assert resp.status_code == 401

    def test_create_booking_invalid_test(self, client, registered_user, centre_and_test):
        resp = client.post("/bookings", json={
            "test_id": "non-existent-test-id",
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"])
        assert resp.status_code == 404

    def test_create_booking_invalid_centre(self, client, registered_user, centre_and_test):
        resp = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": "non-existent-centre-id",
            "appointment_time": future_time(),
        }, headers=registered_user["headers"])
        assert resp.status_code == 404

    def test_create_booking_past_appointment(self, client, registered_user, centre_and_test):
        resp = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": past_time(),
        }, headers=registered_user["headers"])
        assert resp.status_code == 422

    def test_create_booking_test_centre_mismatch(self, client, registered_user, centre_and_test):
        """Test from centre A cannot be booked with centre B."""
        # Create a second centre
        centre2 = client.post("/centres", json={
            "name": "Second Clinic", "location": "Delhi"
        }).json()

        resp = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre2["id"],       # wrong centre
            "appointment_time": future_time(),
        }, headers=registered_user["headers"])
        assert resp.status_code == 400


class TestGetBooking:
    def test_get_own_booking(self, client, registered_user, centre_and_test):
        create = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"])
        booking_id = create.json()["id"]

        resp = client.get(f"/bookings/{booking_id}", headers=registered_user["headers"])
        assert resp.status_code == 200
        assert resp.json()["id"] == booking_id

    def test_get_other_users_booking(self, client, registered_user, centre_and_test):
        """User A cannot access User B's booking."""
        booking_id = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"]).json()["id"]

        # Register user B
        client.post("/auth/signup", json={
            "name": "User B", "email": "b@example.com", "password": "securepass123"
        })
        token_b = client.post("/auth/login", json={
            "email": "b@example.com", "password": "securepass123"
        }).json()["access_token"]

        resp = client.get(f"/bookings/{booking_id}",
                          headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == 403

    def test_get_nonexistent_booking(self, client, registered_user):
        resp = client.get("/bookings/bad-id", headers=registered_user["headers"])
        assert resp.status_code == 404


class TestCancelBooking:
    def test_cancel_pending_booking(self, client, registered_user, centre_and_test):
        booking_id = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"]).json()["id"]

        resp = client.patch(f"/bookings/{booking_id}/cancel",
                            headers=registered_user["headers"])
        assert resp.status_code == 200
        assert resp.json()["status"] == "CANCELLED"

    def test_cancel_already_cancelled(self, client, registered_user, centre_and_test):
        booking_id = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"]).json()["id"]

        client.patch(f"/bookings/{booking_id}/cancel", headers=registered_user["headers"])
        # Second cancel should fail
        resp = client.patch(f"/bookings/{booking_id}/cancel",
                            headers=registered_user["headers"])
        assert resp.status_code == 400

    def test_cancel_unauthorized(self, client, registered_user, centre_and_test):
        booking_id = client.post("/bookings", json={
            "test_id": centre_and_test["test"]["id"],
            "centre_id": centre_and_test["centre"]["id"],
            "appointment_time": future_time(),
        }, headers=registered_user["headers"]).json()["id"]

        resp = client.patch(f"/bookings/{booking_id}/cancel")
        assert resp.status_code == 401


class TestListBookings:
    def test_list_bookings(self, client, registered_user, centre_and_test):
        # Create two bookings
        for _ in range(2):
            client.post("/bookings", json={
                "test_id": centre_and_test["test"]["id"],
                "centre_id": centre_and_test["centre"]["id"],
                "appointment_time": future_time(),
            }, headers=registered_user["headers"])

        resp = client.get("/bookings", headers=registered_user["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
