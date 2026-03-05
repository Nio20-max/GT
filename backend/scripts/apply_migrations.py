from __future__ import annotations

from pathlib import Path
import os
import subprocess


def run() -> None:
    db_url = os.environ.get("GT_DB_URL", "postgresql://gt:gt@localhost:55432/gt")
    migration_files = sorted((Path(__file__).resolve().parents[1] / "migrations").glob("*.sql"))
    if not migration_files:
        raise RuntimeError("No migration files found")

    for migration in migration_files:
        cmd = [
            "psql",
            db_url,
            "-v",
            "ON_ERROR_STOP=1",
            "-f",
            str(migration),
        ]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    run()
