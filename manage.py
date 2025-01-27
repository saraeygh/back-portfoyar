#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def load_env_file(env_file_path=".env.local"):
    try:
        with open(file=env_file_path, mode="r", encoding="utf-8") as env_file:
            for line in env_file:
                line = line.replace("\n", "")
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    except Exception as e:
        print("Loading env vars:")
        print(e)


def main():
    """Run administrative tasks."""
    load_env_file()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
