import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt

from backend.usuarios.domain import InvalidTokenError
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


class JwtTokenAdapterVerificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = JwtTokenAdapter(TEST_SECRET, 5)

    def _encode(self, claims, secret=TEST_SECRET):
        now = datetime.now(timezone.utc)
        base = {"iat": now, "exp": now + timedelta(hours=1)}
        return jwt.encode({**base, **claims}, secret, algorithm="HS256")

    def test_valid_token_returns_user_id(self) -> None:
        token = self.adapter.generar_token(42)
        self.assertEqual(self.adapter.verificar_token(token), 42)

    def test_invalid_tokens_are_rejected(self) -> None:
        now = datetime.now(timezone.utc)
        expired = jwt.encode(
            {"sub": "1", "exp": now - timedelta(hours=1)}, TEST_SECRET, algorithm="HS256"
        )
        cases = {
            "garbage": "not-a-jwt",
            "empty": "",
            "expired": expired,
            "wrong secret": self._encode({"sub": "1"}, "other-secret-that-is-long-enough-xx"),
            "no sub": self._encode({}),
            "non numeric sub": self._encode({"sub": "246F28AB1234"}),
            "device role": self._encode({"sub": "1", "role": "device"}),
            "alg none": jwt.encode({"sub": "1"}, None, algorithm="none"),
        }
        for name, token in cases.items():
            with self.subTest(name), self.assertRaises(InvalidTokenError):
                self.adapter.verificar_token(token)


if __name__ == "__main__":
    unittest.main()
