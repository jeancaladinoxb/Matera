import hashlib
import hmac
import unittest
from unittest.mock import patch

from backend.materas.domain import Mac
from backend.materas.infrastructure.adapters.hmac_claim_verifier import (
    HmacClaimVerifier,
    hmac_claim_verifier_from_environment,
)

KEY = "test-master-key-that-is-long-enough-1234"


class HmacClaimVerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.verifier = HmacClaimVerifier(KEY)

    def test_code_is_first_12_lowercase_hex_of_hmac_sha256(self) -> None:
        expected = hmac.new(KEY.encode(), b"246F28AB1234", hashlib.sha256).hexdigest()[:12]
        codigo = self.verifier.generar(Mac("246F28AB1234"))
        self.assertEqual(codigo, expected)
        self.assertRegex(codigo, r"^[0-9a-f]{12}$")

    def test_correct_code_verifies_for_any_mac_format(self) -> None:
        codigo = self.verifier.generar(Mac("246F28AB1234"))
        for raw in ("246F28AB1234", "24:6F:28:AB:12:34", "246f28ab1234"):
            self.assertTrue(self.verifier.verificar(Mac(raw), codigo))

    def test_wrong_codes_fail(self) -> None:
        codigo = self.verifier.generar(Mac("246F28AB1234"))
        wrong = ("", "000000000000", codigo[:-1], codigo + "0", codigo.upper(), "ñ" * 12, None, 123)
        for value in wrong:
            self.assertFalse(self.verifier.verificar(Mac("246F28AB1234"), value), value)

    def test_code_of_another_mac_fails(self) -> None:
        codigo = self.verifier.generar(Mac("246F28AB1235"))
        self.assertFalse(self.verifier.verificar(Mac("246F28AB1234"), codigo))

    def test_different_master_key_gives_different_code(self) -> None:
        other = HmacClaimVerifier("another-master-key-long-enough-5678-xx")
        mac = Mac("246F28AB1234")
        self.assertNotEqual(self.verifier.generar(mac), other.generar(mac))

    def test_comparison_is_constant_time(self) -> None:
        with patch(
            "backend.materas.infrastructure.adapters.hmac_claim_verifier.hmac.compare_digest",
            return_value=True,
        ) as compare:
            self.assertTrue(self.verifier.verificar(Mac("246F28AB1234"), "anything"))
        compare.assert_called_once()

    def test_short_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "CLAIM_MASTER_KEY"):
            HmacClaimVerifier("short")

    def test_missing_environment_variable_fails_clearly(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "CLAIM_MASTER_KEY"):
                hmac_claim_verifier_from_environment()
        with patch.dict("os.environ", {"CLAIM_MASTER_KEY": KEY}, clear=True):
            self.assertIsInstance(hmac_claim_verifier_from_environment(), HmacClaimVerifier)


if __name__ == "__main__":
    unittest.main()
