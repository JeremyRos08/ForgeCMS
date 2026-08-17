import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from builder.project_generator import GeneratedCMSProjectGenerator


class GeneratedCMSProjectGeneratorTests(SimpleTestCase):
    def test_generator_keeps_public_import_and_generates_compilable_project(self):
        schema = {
            'content_types': [
                {
                    'name': 'Article',
                    'slug': 'article',
                    'fields': [
                        {'name': 'Title', 'slug': 'title', 'type': 'text', 'required': True},
                        {'name': 'Price', 'slug': 'price', 'type': 'number', 'required': False},
                        {'name': 'Published', 'slug': 'published', 'type': 'boolean', 'default': True},
                    ],
                }
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / 'generated_cms'
            generator = GeneratedCMSProjectGenerator(
                schema=schema,
                output_dir=output_dir,
                project_slug='My Generated CMS',
                project_name='My Generated CMS',
            )

            created = generator.generate()

            self.assertEqual(generator.project_slug, 'my_generated_cms')
            self.assertEqual(len(created), 24)
            self.assertTrue((output_dir / 'manage.py').exists())
            self.assertTrue((output_dir / 'my_generated_cms' / 'settings.py').exists())
            self.assertTrue((output_dir / 'content' / 'models.py').exists())
            self.assertTrue((output_dir / 'templates' / 'content' / 'article_list.html').exists())
            self.assertTrue((output_dir / 'static' / 'css' / 'style.css').exists())

            models_code = (output_dir / 'content' / 'models.py').read_text(encoding='utf-8')
            self.assertIn('class Article(models.Model):', models_code)
            self.assertIn('title = models.CharField(max_length=255)', models_code)
            self.assertIn('price = models.DecimalField', models_code)
            self.assertIn('published = models.BooleanField(default=True)', models_code)

            for path in output_dir.rglob('*.py'):
                compile(path.read_text(encoding='utf-8'), str(path), 'exec')

    def test_duplicate_and_reserved_names_are_normalized(self):
        schema = {
            'content_types': [
                {
                    'name': 'Class',
                    'slug': 'class',
                    'fields': [
                        {'name': 'Type', 'slug': 'type', 'type': 'text'},
                        {'name': 'Type again', 'slug': 'type', 'type': 'text'},
                    ],
                },
                {'name': 'Class duplicate', 'slug': 'class', 'fields': []},
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            generator = GeneratedCMSProjectGenerator(schema, temp_dir, project_slug='123 project')

            self.assertEqual(generator.project_slug, 'proj_123_project')
            self.assertEqual(generator.content_types[0]['slug'], 'class')
            self.assertEqual(generator.content_types[1]['slug'], 'class_2')
            self.assertEqual(generator.content_types[0]['fields'][0]['field_name'], 'type_field')
            self.assertEqual(generator.content_types[0]['fields'][1]['field_name'], 'type_field_2')
