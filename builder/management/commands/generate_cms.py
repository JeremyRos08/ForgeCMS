import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from builder.project_generator import GeneratedCMSProjectGenerator
from builder.schema_engine import SchemaEngine


class Command(BaseCommand):
    help = 'Generate a standalone Django CMS project from ForgeCMS Builder schema.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default='generated/forge_cms_generated',
            help='Output directory for the generated project.',
        )
        parser.add_argument(
            '--project-name',
            default='Forge Generated CMS',
            help='Human-readable name of the generated project.',
        )
        parser.add_argument(
            '--project-slug',
            default='forge_generated_cms',
            help='Python module name for the generated Django project.',
        )
        parser.add_argument(
            '--schema-file',
            default='',
            help='Optional path to a schema.json file. If omitted, export from DB.',
        )

    def handle(self, *args, **options):
        output_dir = Path(options['output']).resolve()
        project_name = options['project_name']
        project_slug = options['project_slug']
        schema_file = options['schema_file']

        if output_dir.exists() and any(output_dir.iterdir()):
            raise CommandError(
                f'Output directory is not empty: {output_dir}\n'
                'Choose a new --output path to avoid overwriting existing files.'
            )

        if schema_file:
            schema_path = Path(schema_file).resolve()
            if not schema_path.exists():
                raise CommandError(f'Schema file not found: {schema_path}')
            try:
                schema = json.loads(schema_path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as exc:
                raise CommandError(f'Invalid JSON schema file: {exc}') from exc
        else:
            schema = SchemaEngine().export_schema()

        generator = GeneratedCMSProjectGenerator(
            schema=schema,
            output_dir=output_dir,
            project_slug=project_slug,
            project_name=project_name,
        )
        created_files = generator.generate()

        self.stdout.write(self.style.SUCCESS(f'Generated CMS project at: {output_dir}'))
        self.stdout.write(f'Files created: {len(created_files)}')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write(f'  cd {output_dir}')
        self.stdout.write('  python -m venv .venv')
        self.stdout.write('  .\\.venv\\Scripts\\Activate.ps1')
        self.stdout.write('  pip install -r requirements.txt')
        self.stdout.write('  python manage.py makemigrations')
        self.stdout.write('  python manage.py migrate')
        self.stdout.write('  python manage.py createsuperuser')
        self.stdout.write('  python manage.py runserver')
