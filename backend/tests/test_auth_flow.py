import unittest
from uuid import uuid4

from app import create_app


class AuthFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_cors_allows_loopback_frontend_origin(self):
        response = self.client.get(
            "/api/health",
            headers={"Origin": "http://127.0.0.1:5173"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://127.0.0.1:5173")

    def test_register_and_login_flow(self):
        email = f"flow-{uuid4().hex}@example.com"
        payload = {
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "password": "StrongPass123!",
        }

        register_response = self.client.post("/api/register", json=payload)
        self.assertEqual(register_response.status_code, 201)

        login_response = self.client.post(
            "/api/login",
            json={"email": email, "password": "StrongPass123!"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.get_json()["user"]["email"], email)


if __name__ == "__main__":
    unittest.main()
