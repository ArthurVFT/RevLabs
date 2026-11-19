"""
Import telemetry into RevLabs.

The only accepted input is the first-party JSON format documented in
``TELEMETRY_FORMAT.md``.

Usage:
    python import_telemetry.py [path_to_file.json]

With no path, the bundled seed file (``revlabs/data/telemetry_bundle.json``)
is imported.
"""
import os
import sys
from pathlib import Path

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from revlabs.telemetry_import import run_import_from_json

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = BASE_DIR / 'revlabs' / 'data' / 'telemetry_bundle.json'

SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SOURCE


def main():
    if SOURCE.suffix.lower() != '.json':
        print(f"ERRO: apenas arquivos .json são aceitos: {SOURCE}")
        return 1

    result = run_import_from_json(str(SOURCE))
    return 1 if result.get('error') else 0


if __name__ == '__main__':
    sys.exit(main())
