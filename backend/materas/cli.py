"""Factory registration of materas. Deliberately NOT part of the HTTP API.

Usage (from the repository root):
    python -m backend.materas.cli 24:6F:28:AB:12:34 246f28ab1235

Prints one QR payload per MAC, ``MAT:<MAC12>:<CODIGO>``, on stdout. The code is
a secret derived from CLAIM_MASTER_KEY: do not log or share this output.
"""
import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, TextIO

from dotenv import load_dotenv

from backend.materas.application.ports.output import (
    ClaimCodeVerifierPort,
    MateraRepositoryPort,
)
from backend.materas.domain import InvalidMacError, Mac, Matera


def registrar_materas(
    macs: Sequence[str],
    repository: MateraRepositoryPort,
    verifier: ClaimCodeVerifierPort,
    out: TextIO,
    err: TextIO,
) -> int:
    """Register each MAC as sin_reclamar (idempotent) and print its QR payload.

    Returns the process exit code: 0 if all MACs were valid, 1 otherwise.
    """
    exit_code = 0
    for raw in macs:
        try:
            mac = Mac(raw)
        except InvalidMacError:
            err.write("MAC inválida, se omite: {!r}\n".format(raw))
            exit_code = 1
            continue
        creada = repository.registrar(Matera(mac))
        err.write("{}: {}\n".format(mac.value, "registrada" if creada else "ya existía"))
        out.write("MAT:{}:{}\n".format(mac.value, verifier.generar(mac)))
    return exit_code


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Registra materas de fábrica e imprime su payload QR."
    )
    parser.add_argument("macs", nargs="+", metavar="MAC")
    args = parser.parse_args(argv)

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    from backend.materas.infrastructure.adapters import PostgresMateraRepositoryAdapter
    from backend.materas.infrastructure.adapters.hmac_claim_verifier import (
        hmac_claim_verifier_from_environment,
    )
    from backend.usuarios.infrastructure.adapters.postgresql_repository_adapter import (
        connection_factory_from_environment,
    )

    repository = PostgresMateraRepositoryAdapter(connection_factory_from_environment())
    verifier = hmac_claim_verifier_from_environment()
    return registrar_materas(args.macs, repository, verifier, sys.stdout, sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
