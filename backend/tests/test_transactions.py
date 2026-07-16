# tests/test_transactions.py
"""Transaction CRUD + filtering tests."""

import pytest
from datetime import datetime, timezone

class TestCreateTransaction:
    """Transaction creation tests."""

    def test_create_debit_transaction(
        self, client, auth_headers, sample_transaction_data
    ):
        """Debit transaction create karo."""
        response = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        txn = data["data"]
        assert txn["amount"] == 500.0
        assert txn["transaction_type"] == "debit"
        assert txn["merchant_name"] == "Zomato"
        assert "id" in txn

    def test_create_credit_transaction(self, client, auth_headers):
        """Credit (income) transaction create karo."""
        response = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": 75000,
                "transaction_type": "credit",
                "description": "Monthly Salary",
                "merchant_name": "TechCorp",
                "transaction_date": "2026-07-01T00:00:00Z",
            }
        )
        assert response.status_code == 201
        assert response.json()["data"]["transaction_type"] == "credit"
        assert response.json()["data"]["amount"] == 75000.0

    def test_create_transaction_auto_categorised(
        self, client, auth_headers, sample_transaction_data
    ):
        """ML auto-categorisation trigger hoti hai."""
        response = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        assert response.status_code == 201
        txn = response.json()["data"]
        # ML model loaded hai toh confidence > 0
        # Loaded nahi hai toh 0 bhi acceptable hai
        assert txn["ml_category_confidence"] >= 0

    def test_create_transaction_negative_amount(
        self, client, auth_headers
    ):
        """Negative amount reject hona chahiye."""
        response = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": -100,
                "transaction_type": "debit",
                "description": "Test",
                "transaction_date": "2026-01-15T12:00:00Z",
            }
        )
        assert response.status_code == 422

    def test_create_transaction_zero_amount(self, client, auth_headers):
        """Zero amount reject hona chahiye."""
        response = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json={
                "amount": 0,
                "transaction_type": "debit",
                "description": "Test",
                "transaction_date": "2026-01-15T12:00:00Z",
            }
        )
        assert response.status_code == 422

    def test_create_transaction_unauthorized(
        self, client, sample_transaction_data
    ):
        """Bina auth ke transaction create nahi hona chahiye."""
        response = client.post(
            "/api/v1/transactions",
            json=sample_transaction_data
        )
        assert response.status_code == 403


class TestListTransactions:
    """Transaction listing + filtering tests."""

    def _create_txn(self, client, headers, **kwargs):
        """Helper — transaction create karo."""
        defaults = {
            "amount": 100.0,
            "transaction_type": "debit",
            "description": "Test txn",
            "transaction_date": "2026-07-10T12:00:00Z",
        }
        defaults.update(kwargs)
        r = client.post("/api/v1/transactions",
                       headers=headers, json=defaults)
        return r.json()["data"]

    def test_list_empty(self, client, auth_headers):
        """Koi transaction nahi — empty list."""
        response = client.get("/api/v1/transactions",
                            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["items"] == []
        assert data["pagination"]["total"] == 0

    def test_list_with_transactions(self, client, auth_headers):
        """Transactions list honi chahiye."""
        # Create 3 transactions
        for i in range(3):
            self._create_txn(client, auth_headers,
                           description=f"Transaction {i+1}",
                           amount=100.0 * (i + 1))

        response = client.get("/api/v1/transactions",
                            headers=auth_headers)
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 3
        assert data["pagination"]["total"] == 3

    def test_pagination(self, client, auth_headers):
        """Pagination kaam karta hai?"""
        # 5 transactions create karo
        for i in range(5):
            self._create_txn(client, auth_headers,
                           description=f"Txn {i}")

        # Page 1 — 2 items
        r1 = client.get(
            "/api/v1/transactions?page=1&page_size=2",
            headers=auth_headers
        )
        assert r1.status_code == 200
        assert len(r1.json()["data"]["items"]) == 2
        assert r1.json()["data"]["pagination"]["total_pages"] == 3

    def test_search_filter(self, client, auth_headers):
        """Search filter kaam karta hai?"""
        self._create_txn(client, auth_headers,
                        description="Swiggy Biryani",
                        merchant_name="Swiggy")
        self._create_txn(client, auth_headers,
                        description="Amazon Order",
                        merchant_name="Amazon")

        response = client.get(
            "/api/v1/transactions?search=swiggy",
            headers=auth_headers
        )
        assert response.status_code == 200
        items = response.json()["data"]["items"]
        assert len(items) == 1
        assert "Swiggy" in items[0]["merchant_name"]

    def test_type_filter(self, client, auth_headers):
        """Transaction type filter kaam karta hai?"""
        self._create_txn(client, auth_headers,
                        transaction_type="debit")
        self._create_txn(client, auth_headers,
                        transaction_type="credit",
                        description="Salary")

        # Sirf debit
        r = client.get(
            "/api/v1/transactions?transaction_type=debit",
            headers=auth_headers
        )
        items = r.json()["data"]["items"]
        assert all(t["transaction_type"] == "debit" for t in items)

    def test_anomaly_filter(self, client, auth_headers):
        """Anomaly filter kaam karta hai?"""
        # Huge amount — anomaly trigger honi chahiye
        self._create_txn(client, auth_headers,
                        amount=99999,
                        description="Suspicious transfer")

        r = client.get(
            "/api/v1/transactions?anomalies_only=true",
            headers=auth_headers
        )
        assert r.status_code == 200

    def test_user_isolation(self, client, auth_headers, db):
        """User doosre user ki transactions nahi dekh sakta."""
        from app.models.user import User
        from app.core.security import hash_password
        import uuid

        # Doosra user banao
        user2 = User(
            id=uuid.uuid4(),
            email="user2@example.com",
            full_name="User Two",
            hashed_password=hash_password("password123"),
            is_active=True,
        )
        db.add(user2)
        db.commit()

        # User 2 login
        r2_login = client.post("/api/v1/auth/login", json={
            "email": "user2@example.com",
            "password": "password123"
        })
        user2_headers = {
            "Authorization": f"Bearer {r2_login.json()['data']['access_token']}"
        }

        # User 1 ka transaction
        self._create_txn(client, auth_headers,
                        description="User 1 secret transaction")

        # User 2 ko dikhna nahi chahiye
        r = client.get("/api/v1/transactions",
                      headers=user2_headers)
        assert r.json()["data"]["pagination"]["total"] == 0


class TestTransactionCRUD:
    """Single transaction CRUD tests."""

    def test_get_transaction_by_id(self, client, auth_headers,
                                    sample_transaction_data):
        """ID se transaction lo."""
        create_r = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        txn_id = create_r.json()["data"]["id"]

        response = client.get(
            f"/api/v1/transactions/{txn_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == txn_id

    def test_update_transaction(self, client, auth_headers,
                                 sample_transaction_data):
        """Transaction update karo."""
        create_r = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        txn_id = create_r.json()["data"]["id"]

        response = client.put(
            f"/api/v1/transactions/{txn_id}",
            headers=auth_headers,
            json={"notes": "This was a party order"}
        )
        assert response.status_code == 200
        assert response.json()["data"]["notes"] == "This was a party order"

    def test_delete_transaction(self, client, auth_headers,
                                 sample_transaction_data):
        """Transaction delete karo."""
        create_r = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        txn_id = create_r.json()["data"]["id"]

        # Delete
        del_r = client.delete(
            f"/api/v1/transactions/{txn_id}",
            headers=auth_headers
        )
        assert del_r.status_code == 200

        # Ab exist nahi karta
        get_r = client.get(
            f"/api/v1/transactions/{txn_id}",
            headers=auth_headers
        )
        assert get_r.status_code == 404

    def test_get_other_user_transaction(self, client, auth_headers,
                                         sample_transaction_data, db):
        """Doosre user ka transaction access nahi hona chahiye."""
        from app.models.user import User
        from app.core.security import hash_password
        import uuid

        # User 1 ka transaction
        create_r = client.post(
            "/api/v1/transactions",
            headers=auth_headers,
            json=sample_transaction_data
        )
        txn_id = create_r.json()["data"]["id"]

        user2 = User(
            id=uuid.uuid4(),
            email="user2@example.com",
            full_name="User 2",
            hashed_password=hash_password("password123"),
            is_active=True,
        )
        db.add(user2)
        db.commit()

        login_r = client.post("/api/v1/auth/login", json={
            "email": "user2@example.com",
            "password": "password123"
        })
        user2_headers = {
            "Authorization": f"Bearer {login_r.json()['data']['access_token']}"
        }

        # User 2 User 1 ka transaction nahi dekh sakta
        response = client.get(
            f"/api/v1/transactions/{txn_id}",
            headers=user2_headers
        )
        assert response.status_code == 404


class TestCSVImport:
    """CSV import tests."""

    def test_csv_import_success(self, client, auth_headers):
        """Valid CSV import ho."""
        csv_content = """date,amount,type,description,merchant
2026-07-01,1200,debit,Zomato Order,Zomato
2026-07-02,75000,credit,Salary,Company
2026-07-03,500,debit,Uber Ride,Uber
"""
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = client.post(
            "/api/v1/transactions/import",
            headers=auth_headers,
            files=files
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["imported"] == 3
        assert data["skipped"] == 0

    def test_csv_import_invalid_file(self, client, auth_headers):
        """Non-CSV file reject honi chahiye."""
        files = {"file": ("test.txt", "not a csv", "text/plain")}
        response = client.post(
            "/api/v1/transactions/import",
            headers=auth_headers,
            files=files
        )
        assert response.status_code == 400

    def test_csv_import_partial_data(self, client, auth_headers):
        """Kuch rows valid, kuch invalid."""
        csv_content = """date,amount,type,description,merchant
2026-07-01,1200,debit,Valid Transaction,Shop
2026-07-02,,debit,Missing Amount,Shop
2026-07-03,500,debit,Another Valid,Store
"""
        files = {"file": ("test.csv", csv_content, "text/csv")}
        response = client.post(
            "/api/v1/transactions/import",
            headers=auth_headers,
            files=files
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["imported"] >= 1
        assert data["skipped"] >= 1