"""Tests for payment and webhook endpoints."""
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch


def future_time(hours: int = 24) -> str:
    dt = datetime.now(timezone.utc) + timedelta(hours=hours)
    return dt.isoformat()


def make_booking(client, headers, centre_and_test) -> dict:
    resp = client.post("/bookings", json={
        "test_id": centre_and_test["test"]["id"],
        "centre_id": centre_and_test["centre"]["id"],
        "appointment_time": future_time(),
    }, headers=headers)
    assert resp.status_code == 201
    return resp.json()


class TestInitiatePayment:
    def test_payment_changes_booking_status(self, client, registered_user, centre_and_test):
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        booking_id = booking["id"]

        resp = client.post("/payments", json={"booking_id": booking_id},
                           headers=registered_user["headers"])
        assert resp.status_code == 201
        payment = resp.json()
        assert payment["status"] in ("SUCCESS", "FAILED")
        assert payment["booking_id"] == booking_id

        # Booking status should reflect payment outcome
        booking_resp = client.get(f"/bookings/{booking_id}",
                                  headers=registered_user["headers"])
        expected_status = "CONFIRMED" if payment["status"] == "SUCCESS" else "FAILED"
        assert booking_resp.json()["status"] == expected_status

    def test_payment_success_path(self, client, registered_user, centre_and_test):
        """Force SUCCESS via mock."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)

        with patch("app.services.payment_service.random") as mock_random:
            mock_random.random.return_value = 0.1  # < 0.7 → SUCCESS
            resp = client.post("/payments", json={"booking_id": booking["id"]},
                               headers=registered_user["headers"])
        assert resp.status_code == 201
        assert resp.json()["status"] == "SUCCESS"

    def test_payment_failure_path(self, client, registered_user, centre_and_test):
        """Force FAILED via mock."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)

        with patch("app.services.payment_service.random") as mock_random:
            mock_random.random.return_value = 0.9  # >= 0.7 → FAILED
            resp = client.post("/payments", json={"booking_id": booking["id"]},
                               headers=registered_user["headers"])
        assert resp.status_code == 201
        assert resp.json()["status"] == "FAILED"

    def test_payment_invalid_booking(self, client, registered_user):
        resp = client.post("/payments", json={"booking_id": "nonexistent-id"},
                           headers=registered_user["headers"])
        assert resp.status_code == 404

    def test_payment_already_paid_booking(self, client, registered_user, centre_and_test):
        """Cannot pay a booking that's already CONFIRMED/FAILED."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        # First payment
        client.post("/payments", json={"booking_id": booking["id"]},
                    headers=registered_user["headers"])
        # Second payment attempt on non-PENDING booking
        resp = client.post("/payments", json={"booking_id": booking["id"]},
                           headers=registered_user["headers"])
        assert resp.status_code == 400

    def test_payment_unauthenticated(self, client, registered_user, centre_and_test):
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        resp = client.post("/payments", json={"booking_id": booking["id"]})
        assert resp.status_code == 401

    def test_payment_other_users_booking(self, client, registered_user, centre_and_test):
        booking = make_booking(client, registered_user["headers"], centre_and_test)

        client.post("/auth/signup", json={
            "name": "User B", "email": "b@example.com", "password": "securepass123"
        })
        token_b = client.post("/auth/login", json={
            "email": "b@example.com", "password": "securepass123"
        }).json()["access_token"]

        resp = client.post("/payments", json={"booking_id": booking["id"]},
                           headers={"Authorization": f"Bearer {token_b}"})
        assert resp.status_code == 403


class TestWebhook:
    def _webhook_payload(self, booking_id: str, status: str = "SUCCESS") -> dict:
        return {
            "event_id": str(uuid.uuid4()),
            "booking_id": booking_id,
            "status": status,
            "amount": "750.00",
        }

    def test_webhook_success_updates_booking(self, client, registered_user, centre_and_test):
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        payload = self._webhook_payload(booking["id"], "SUCCESS")

        resp = client.post("/payments/webhook", json=payload)
        assert resp.status_code == 200
        assert resp.json()["received"] is True

        booking_resp = client.get(f"/bookings/{booking['id']}",
                                  headers=registered_user["headers"])
        assert booking_resp.json()["status"] == "CONFIRMED"

    def test_webhook_failed_updates_booking(self, client, registered_user, centre_and_test):
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        payload = self._webhook_payload(booking["id"], "FAILED")

        resp = client.post("/payments/webhook", json=payload)
        assert resp.status_code == 200

        booking_resp = client.get(f"/bookings/{booking['id']}",
                                  headers=registered_user["headers"])
        assert booking_resp.json()["status"] == "FAILED"

    def test_webhook_idempotent_duplicate(self, client, registered_user, centre_and_test):
        """The SAME event_id sent twice must be a no-op on the second call."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        payload = self._webhook_payload(booking["id"], "SUCCESS")

        resp1 = client.post("/payments/webhook", json=payload)
        resp2 = client.post("/payments/webhook", json=payload)  # duplicate

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Both return received=True (idempotent)
        assert resp2.json()["received"] is True
        assert "already processed" in resp2.json()["message"].lower()

        # Booking should be CONFIRMED (not double-changed)
        booking_resp = client.get(f"/bookings/{booking['id']}",
                                  headers=registered_user["headers"])
        assert booking_resp.json()["status"] == "CONFIRMED"

    def test_webhook_invalid_booking_id(self, client):
        payload = {
            "event_id": str(uuid.uuid4()),
            "booking_id": "nonexistent",
            "status": "SUCCESS",
            "amount": "750.00",
        }
        resp = client.post("/payments/webhook", json=payload)
        assert resp.status_code == 404

    def test_webhook_terminal_booking_rejected(self, client, registered_user, centre_and_test):
        """Webhook for a CANCELLED booking should be rejected."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)
        # Cancel the booking
        client.patch(f"/bookings/{booking['id']}/cancel",
                     headers=registered_user["headers"])

        payload = self._webhook_payload(booking["id"], "SUCCESS")
        resp = client.post("/payments/webhook", json=payload)
        assert resp.status_code == 400

    def test_webhook_unique_event_ids_both_processed(self, client, registered_user, centre_and_test):
        """Two different event_ids for the same booking are both attempted (second will be blocked by state)."""
        booking = make_booking(client, registered_user["headers"], centre_and_test)

        payload1 = self._webhook_payload(booking["id"], "SUCCESS")
        resp1 = client.post("/payments/webhook", json=payload1)
        assert resp1.status_code == 200

        # Second event for same booking — booking is now CONFIRMED
        payload2 = self._webhook_payload(booking["id"], "FAILED")
        # The booking is in a terminal-ish state but still CONFIRMED — not PENDING
        # Service should reject this with 400
        resp2 = client.post("/payments/webhook", json=payload2)
        assert resp2.status_code == 400
