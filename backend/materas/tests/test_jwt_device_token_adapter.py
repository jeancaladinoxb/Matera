import unittest
from unittest.mock import patch

import jwt

from backend.materas.domain import Mac
from backend.materas.infrastructure.adapters.jwt_device_token_adapter import (
    JwtDeviceTokenAdapter,
    jwt_device_token_adapter_from_environment,
)
from backend.usuarios.domain import InvalidTokenError
from backend.usuarios.infrastructure.adapters import JwtTokenAdapter

DEVICE_SECRET = "device-secret-that-is-long-enough-for-hs256"
USER_SECRET = "user-secret-that-is-long-enough-for-hs256-x"


class JwtDeviceTokenAdapterTests(unittest.TestCase):
    def test_token_claims(self) -> None:
        token = JwtDeviceTokenAdapter(DEVICE_SECRET, 365).generar_token(Mac("24:6f:28:ab:12:34"))
        claims = jwt.decode(token, DEVICE_SECRET, algorithms=["HS256"])
        self.assertEqual(claims["sub"], "246F28AB1234")
        self.assertEqual(claims["role"], "device")
        self.assertEqual(claims["exp"] - claims["iat"], 365 * 24 * 60 * 60)

    def test_default_expiration_is_365_days(self) -> None:
        env = {"DEVICE_JWT_SECRET": DEVICE_SECRET, "JWT_SECRET": USER_SECRET}
        with patch.dict("os.environ", env, clear=True):
            adapter = jwt_device_token_adapter_from_environment()
        claims = jwt.decode(adapter.generar_token(Mac("246F28AB1234")), DEVICE_SECRET, algorithms=["HS256"])
        self.assertEqual(claims["exp"] - claims["iat"], 365 * 24 * 60 * 60)

    def test_expiration_is_configurable(self) -> None:
        env = {"DEVICE_JWT_SECRET": DEVICE_SECRET, "DEVICE_JWT_EXPIRATION_DAYS": "30"}
        with patch.dict("os.environ", env, clear=True):
            adapter = jwt_device_token_adapter_from_environment()
        claims = jwt.decode(adapter.generar_token(Mac("246F28AB1234")), DEVICE_SECRET, algorithms=["HS256"])
        self.assertEqual(claims["exp"] - claims["iat"], 30 * 24 * 60 * 60)

    def test_configuration_errors(self) -> None:
        cases = [
            ({}, "DEVICE_JWT_SECRET"),
            ({"DEVICE_JWT_SECRET": DEVICE_SECRET, "JWT_SECRET": DEVICE_SECRET}, "distinto"),
            ({"DEVICE_JWT_SECRET": DEVICE_SECRET, "DEVICE_JWT_EXPIRATION_DAYS": "x"}, "DEVICE_JWT_EXPIRATION_DAYS"),
            ({"DEVICE_JWT_SECRET": DEVICE_SECRET, "DEVICE_JWT_EXPIRATION_DAYS": "0"}, "DEVICE_JWT_EXPIRATION_DAYS"),
            ({"DEVICE_JWT_SECRET": "short"}, "DEVICE_JWT_SECRET"),
        ]
        for env, message in cases:
            with self.subTest(env), patch.dict("os.environ", env, clear=True):
                with self.assertRaisesRegex(ValueError, message):
                    jwt_device_token_adapter_from_environment()

    def test_device_token_is_not_accepted_as_user_token(self) -> None:
        device_token = JwtDeviceTokenAdapter(DEVICE_SECRET).generar_token(Mac("246F28AB1234"))
        with self.assertRaises(InvalidTokenError):
            JwtTokenAdapter(USER_SECRET, 5).verificar_token(device_token)
        # Even if both were signed with the same secret, the role is rejected.
        with self.assertRaises(InvalidTokenError):
            JwtTokenAdapter(DEVICE_SECRET, 5).verificar_token(device_token)

    def test_user_token_is_not_accepted_as_device_token(self) -> None:
        user_token = JwtTokenAdapter(USER_SECRET, 5).generar_token(1)
        with self.assertRaises(jwt.InvalidSignatureError):
            jwt.decode(user_token, DEVICE_SECRET, algorithms=["HS256"])
        self.assertNotIn("role", jwt.decode(user_token, USER_SECRET, algorithms=["HS256"]))


if __name__ == "__main__":
    unittest.main()
