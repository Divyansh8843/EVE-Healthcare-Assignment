"""Tests for diagnostic centres and tests endpoints."""


class TestCentres:
    def test_list_centres_empty(self, client):
        resp = client.get("/centres")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_create_and_list_centre(self, client):
        client.post("/centres", json={"name": "HealthLab", "location": "Bangalore"})
        resp = client.get("/centres")
        assert resp.json()["total"] == 1

    def test_get_centre_with_tests(self, client, centre_and_test):
        centre_id = centre_and_test["centre"]["id"]
        resp = client.get(f"/centres/{centre_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["tests"]) == 1
        assert data["tests"][0]["price"] == "750.00"

    def test_get_nonexistent_centre(self, client):
        resp = client.get("/centres/bad-id")
        assert resp.status_code == 404

    def test_create_centre_blank_name(self, client):
        resp = client.post("/centres", json={"name": "  ", "location": "Delhi"})
        assert resp.status_code == 422

    def test_pagination(self, client):
        for i in range(5):
            client.post("/centres", json={"name": f"Lab {i}", "location": "City"})
        resp = client.get("/centres?page=1&page_size=3")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["items"]) == 3


class TestDiagnosticTests:
    def test_list_tests_empty(self, client):
        resp = client.get("/tests")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_create_test_for_centre(self, client, centre_and_test):
        test = centre_and_test["test"]
        assert test["name"] == "Complete Blood Count"
        assert float(test["price"]) == 750.0

    def test_create_test_invalid_centre(self, client):
        resp = client.post("/tests", json={
            "centre_id": "nonexistent",
            "name": "Lipid Panel",
            "price": "500.00",
        })
        assert resp.status_code == 404

    def test_create_test_negative_price(self, client, centre_and_test):
        resp = client.post("/tests", json={
            "centre_id": centre_and_test["centre"]["id"],
            "name": "Bad Test",
            "price": "-50.00",
        })
        assert resp.status_code == 422

    def test_filter_tests_by_centre(self, client, centre_and_test):
        centre_id = centre_and_test["centre"]["id"]
        resp = client.get(f"/tests?centre_id={centre_id}")
        assert resp.json()["total"] == 1

    def test_get_test(self, client, centre_and_test):
        test_id = centre_and_test["test"]["id"]
        resp = client.get(f"/tests/{test_id}")
        assert resp.status_code == 200

    def test_get_nonexistent_test(self, client):
        resp = client.get("/tests/bad-id")
        assert resp.status_code == 404
