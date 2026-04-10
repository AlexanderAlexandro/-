from __future__ import annotations

import argparse
from pathlib import Path

from backend.config import get_settings
from backend.database import build_database
from backend.server import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Mini Messenger MVP")
    parser.add_argument(
        "command",
        nargs="?",
        choices=("runserver", "init-db", "seed-db"),
        default="runserver",
    )
    args = parser.parse_args()

    if args.command == "runserver":
        run()
        return

    project_root = Path(__file__).resolve().parent
    settings = get_settings(project_root)
    database = build_database(settings, project_root)

    if args.command == "init-db":
        database.init_schema()
        print(f"Database schema created at {settings.database_path}")
        return

    if args.command == "seed-db":
        database.seed_demo_data()
        print(f"Seed data loaded into {settings.database_path}")


if __name__ == "__main__":
    main()
