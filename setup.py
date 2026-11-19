"""
One-time project setup for fresh clones.

Usage:
    python setup.py

Runs, in order:
    1. manage.py migrate
    2. populate_data.py          (cars + tracks)
    3. populateparts.py          (mod parts catalog)
    4. populate_gt7_parts.py     (extra GT7 parts)
    5. populate_adjustments.py   (adjustable parts)
    6. import_telemetry.py       (bundled JSON telemetry)
    7. manage.py createsuperuser (interactive, optional)
"""
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON = sys.executable

TOTAL_STEPS = 6


def run_step(label, script, args=None):
    print(f"\n{'=' * 60}")
    print(f"  {label}")
    print(f"{'=' * 60}")
    cmd = [PYTHON, script] + (args or [])
    result = subprocess.run(cmd, cwd=BASE_DIR)
    if result.returncode != 0:
        print(f"\n  ERRO: '{script}' falhou (código {result.returncode})")
        sys.exit(result.returncode)
    print("  OK")


def main():
    print(f"{'=' * 60}")
    print("  RevLabs — Fresh Clone Setup")
    print(f"{'=' * 60}")

    run_step(f"1/{TOTAL_STEPS}  Applying database migrations...", "manage.py", ["migrate"])
    run_step(f"2/{TOTAL_STEPS}  Seeding cars and tracks...", "populate_data.py")
    run_step(f"3/{TOTAL_STEPS}  Seeding mod parts...", "populateparts.py")
    run_step(f"4/{TOTAL_STEPS}  Seeding GT7 parts...", "populate_gt7_parts.py")
    run_step(f"5/{TOTAL_STEPS}  Seeding adjustable parts...", "populate_adjustments.py")

    telemetry_bundle = os.path.join(BASE_DIR, 'revlabs', 'data', 'telemetry_bundle.json')
    if os.path.exists(telemetry_bundle):
        run_step(f"{TOTAL_STEPS}/{TOTAL_STEPS}  Importing bundled telemetry...", "import_telemetry.py", [telemetry_bundle])
        print(f"\n  Telemetry imported from {telemetry_bundle}")
    else:
        print(f"\n  Telemetry bundle not found at {telemetry_bundle}")
        print("  Provide telemetry later with: python import_telemetry.py <file.json>")

    print(f"\n{'=' * 60}")
    print("  Setup complete!")
    print("  Run: python manage.py runserver")
    print(f"{'=' * 60}")

    try:
        resp = input("\n  Create a superuser now? (y/N): ").strip().lower()
        if resp == 'y':
            subprocess.run([PYTHON, 'manage.py', 'createsuperuser'], cwd=BASE_DIR)
    except (EOFError, KeyboardInterrupt):
        pass


if __name__ == '__main__':
    main()
