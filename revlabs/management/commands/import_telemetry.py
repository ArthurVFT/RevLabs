from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from revlabs.telemetry_import import run_import_from_json


class Command(BaseCommand):
    help = 'Import telemetry laps from a RevLabs JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_path',
            nargs='?',
            default=str(Path(settings.BASE_DIR) / 'revlabs' / 'data' / 'telemetry_bundle.json'),
            help='Path to a .json file (defaults to the bundled seed file)',
        )

    def handle(self, *args, **options):
        json_path = options['json_path']
        if not json_path.lower().endswith('.json'):
            self.stderr.write(self.style.ERROR(f'Apenas arquivos .json são aceitos: {json_path}'))
            return

        result = run_import_from_json(json_path, print_func=self.stdout.write)
        if result.get('error'):
            self.stderr.write(self.style.ERROR(result['error']))
