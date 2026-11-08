import unittest

from backend.usuarios.domain import (
    Email,
    InvalidEmailError,
    InvalidPasswordError,
    MissingRequiredFieldError,
    Password,
    Usuario,
)


class EmailTests(unittest.TestCase):
    def test_accepts_valid_email(self) -> None:
        self.assertEqual(
            Email("ana.perez+test@example.com").value,
            "ana.perez+test@example.com",
        )

    def test_normalizes_email_before_validation(self) -> None:
        self.assertEqual(Email("  Ana.Perez@Example.COM ").value, "ana.perez@example.com")

    def test_rejects_invalid_email_formats(self) -> None:
        invalid_emails = (
            "",
            "ana.example.com",
            "ana@",
            "@example.com",
            "ana..perez@example.com",
            "ana@example",
        )
        for value in invalid_emails:
            with self.subTest(value=value):
                with self.assertRaises(InvalidEmailError):
                    Email(value)

    def test_rejects_non_string_value(self) -> None:
        with self.assertRaises(InvalidEmailError):
            Email(None)  # type: ignore[arg-type]

    def test_rejects_address_longer_than_254_characters(self) -> None:
        with self.assertRaises(InvalidEmailError):
            Email("{}@example.com".format("a" * 243))


class PasswordTests(unittest.TestCase):
    def test_accepts_alphanumeric_password_with_uppercase(self) -> None:
        self.assertEqual(Password("Clave123").value, "Clave123")

    def test_accepts_password_with_only_uppercase_letters(self) -> None:
        self.assertEqual(Password("CLAVEABC").value, "CLAVEABC")

    def test_rejects_password_without_uppercase(self) -> None:
        with self.assertRaises(InvalidPasswordError):
            Password("clave123")

    def test_rejects_non_alphanumeric_password(self) -> None:
        for value in ("Clave 123", "Clave-123", "", "CLAVE"):
            with self.subTest(value=value):
                with self.assertRaises(InvalidPasswordError):
                    Password(value)

    def test_rejects_non_string_value(self) -> None:
        with self.assertRaises(InvalidPasswordError):
            Password(None)  # type: ignore[arg-type]

    def test_password_is_not_in_repr(self) -> None:
        self.assertNotIn("Clave123", repr(Password("Clave123")))


class UsuarioTests(unittest.TestCase):
    def test_contains_domain_value_objects(self) -> None:
        user = Usuario(
            nombre="Ana",
            apellido="Pérez",
            nickname="anap",
            correo=Email("ana@example.com"),
            contrasena=Password("Clave123"),
        )

        self.assertEqual(user.nombre, "Ana")
        self.assertEqual(user.apellido, "Pérez")
        self.assertEqual(user.nickname, "anap")
        self.assertEqual(user.correo, Email("ana@example.com"))
        self.assertEqual(user.contrasena, Password("Clave123"))
        self.assertNotIn("Clave123", repr(user))

    def test_rejects_missing_required_text_fields(self) -> None:
        for field_name in ("nombre", "apellido", "nickname"):
            fields = {
                "nombre": "Ana",
                "apellido": "Pérez",
                "nickname": "anap",
                "correo": Email("ana@example.com"),
                "contrasena": Password("Clave123"),
            }
            fields[field_name] = "   "
            with self.subTest(field=field_name):
                with self.assertRaises(MissingRequiredFieldError):
                    Usuario(**fields)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
