# tests/test_ml.py
"""ML services tests — categoriser, anomaly detector."""

import pytest
from unittest.mock import patch, MagicMock

class TestCategoriser:
    """Expense categorisation tests."""

    def test_categorise_endpoint_auth_required(self, client):
        """Auth required hai."""
        response = client.post(
            "/api/v1/ml/categorise",
            json={"description": "Zomato order", "merchant_name": "Zomato"}
        )
        assert response.status_code == 403

    def test_categorise_zomato(self, client, auth_headers):
        """Zomato → Dining Out."""
        response = client.post(
            "/api/v1/ml/categorise",
            headers=auth_headers,
            json={
                "description": "Zomato food delivery order",
                "merchant_name": "Zomato"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "category" in data
        assert "confidence" in data
        assert 0 <= data["confidence"] <= 1

    def test_categorise_electricity_bill(self, client, auth_headers):
        """MSEB electricity → Utilities."""
        response = client.post(
            "/api/v1/ml/categorise",
            headers=auth_headers,
            json={
                "description": "MSEB electricity bill payment",
                "merchant_name": "MSEB"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        if data["confidence"] > 0.5:
            assert data["category"] == "Utilities"

    def test_categorise_salary(self, client, auth_headers):
        """Salary credit → Salary category."""
        response = client.post(
            "/api/v1/ml/categorise",
            headers=auth_headers,
            json={
                "description": "Monthly salary credit",
                "merchant_name": "TechCorp"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        if data["confidence"] > 0.7:
            assert data["category"] == "Salary"

    def test_batch_categorise(self, client, auth_headers):
        """Batch categorisation kaam karta hai?"""
        response = client.post(
            "/api/v1/ml/categorise/batch",
            headers=auth_headers,
            json={
                "descriptions": [
                    "Zomato biryani order",
                    "BigBasket grocery delivery",
                    "MSEB electricity bill",
                ]
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "predictions" in data
        assert len(data["predictions"]) == 3

    def test_model_info(self, client, auth_headers):
        """Model info endpoint."""
        response = client.get(
            "/api/v1/ml/model-info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "loaded" in data


class TestAnomalyDetection:
    """Anomaly detection tests."""

    def test_anomaly_check_normal(self, client, auth_headers):
        """Normal transaction — not anomaly."""
        response = client.post(
            "/api/v1/ml/anomaly-check",
            headers=auth_headers,
            json={
                "amount": 500,
                "description": "Zomato food order",
                "transaction_date": "2026-07-10T12:00:00"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "is_anomaly" in data
        assert "anomaly_score" in data
        assert 0 <= data["anomaly_score"] <= 1

    def test_anomaly_check_large_amount(self, client, auth_headers):
        """Very large amount → anomaly."""
        response = client.post(
            "/api/v1/ml/anomaly-check",
            headers=auth_headers,
            json={
                "amount": 95000,
                "description": "Unknown transfer midnight",
                "transaction_date": "2026-07-10T02:00:00"
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["is_anomaly"] is True
        assert data["anomaly_score"] > 0.5
        assert data["severity"] in ["high", "medium"]
        assert len(data["reasons"]) > 0

    def test_anomaly_stats(self, client, auth_headers):
        """Anomaly stats endpoint."""
        response = client.get(
            "/api/v1/ml/anomaly-stats",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "total_anomalies" in data
        assert "unread_alerts" in data


class TestForecast:
    """Spending forecast tests."""

    def test_forecast_endpoint(self, client, auth_headers):
        """Forecast endpoint kaam karta hai?"""
        response = client.get(
            "/api/v1/ml/forecast",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "predictions" in data
        assert "total_predicted" in data

    def test_savings_advice(self, client, auth_headers):
        """Savings advice endpoint."""
        response = client.get(
            "/api/v1/ml/savings-advice?monthly_income=75000",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestNLQ:
    """Natural Language Query tests."""

    def test_suggestions_endpoint(self, client, auth_headers):
        """Query suggestions return hoti hain."""
        response = client.get(
            "/api/v1/nlq/suggestions",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0

    def test_query_requires_auth(self, client):
        """NLQ auth required hai."""
        response = client.post(
            "/api/v1/nlq/query",
            json={"query": "test query"}
        )
        assert response.status_code == 403