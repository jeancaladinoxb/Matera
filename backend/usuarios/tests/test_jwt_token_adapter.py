import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt

from backend.usuarios.infrastructure.adapters.jwt_token_adapter import (
    JwtTokenAdapter,
    jwt_token_adapter_from_environment,
)


TEST_SECRET = "test-secret-that-is-long-enough-for-hs256"


class JwtTokenAdapterTests(unittest.TestCase):
    def test_token_contains_user_id_and_timestamps(self) -> None:
        with patch.dict(
            os.environ,
            {"JWT_SECRET": TEST_SECRET, "JWT_EXPIRATION_HOURS": "5"},
            clear=True,
        ):
            adapter = jwt_token_adapter_from_environment()

        token = adapter.generar_token(123)
        claims = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])

        self.assertEqual(claims["sub"], "123")
        self.assertIsInstance(claims["iat"], int)
        self.assertIsInstance(claims["exp"], int)
        self.assertEqual(claims["exp"] - claims["iat"], 5 * 60 * 60)

    def test_expiration_hours_can_be_configured_by_environment(self) -> None:
        with patch.dict(
            os.environ,
            {"JWT_SECRET": TEST_SECRET, "JWT_EXPIRATION_HOURS": "2"},
            clear=True,
        ):
            adapter = jwt_token_adapter_from_environment()

        claims = jwt.decode(
            adapter.generar_token(10),
            TEST_SECRET,
            algorithms=["HS256"],
        )
        self.assertEqual(claims["exp"] - claims["iat"], 2 * 60 * 60)

    def test_missing_secret_fails_clearly(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "JWT_SECRET"):
                jwt_token_adapter_from_environment()

    def test_non_positive_expiration_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "JWT_EXPIRATION_HOURS"):
            JwtTokenAdapter(secret=TEST_SECRET, expiration_hours=0)

    def test_expired_token_fails_decoding(self) -> None:
        now = datetime.now(timezone.utc)
        expired_token = jwt.encode(
            {
                "sub": "123",
                "iat": now - timedelta(hours=2),
                "exp": now - timedelta(hours=1),
            },
            TEST_SECRET,
            algorithm="HS256",
        )

        with self.assertRaises(jwt.ExpiredSignatureError):
            jwt.decode(expired_token, TEST_SECRET, algorithms=["HS256"])


if __name__ == "__main__":
    unittest.main()
