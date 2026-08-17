from django.test import TestCase

from builder.models import BuilderSnapshot, CustomContentType, CustomField
from builder.schema_engine import SchemaEngine


class SchemaEngineTests(TestCase):
    def test_export_schema_contains_active_types_and_fields(self):
        article = CustomContentType.objects.create(name='Article', slug='article')
        CustomField.objects.create(
            content_type=article,
            name='Title',
            slug='title',
            field_type='text',
            required=True,
            order=0,
        )
        CustomContentType.objects.create(name='Hidden', slug='hidden', is_active=False)

        schema = SchemaEngine().export_schema()

        self.assertEqual(len(schema['content_types']), 1)
        self.assertEqual(schema['content_types'][0]['slug'], 'article')
        self.assertEqual(schema['content_types'][0]['fields'][0]['slug'], 'title')

    def test_apply_snapshot_updates_schema_and_disables_missing_types(self):
        old_type = CustomContentType.objects.create(name='Old', slug='old')
        snapshot = BuilderSnapshot.objects.create(
            name='Snapshot test',
            schema={
                'content_types': [
                    {
                        'name': 'Article',
                        'slug': 'article',
                        'description': 'Articles du site',
                        'config': {'strict_fields': True},
                        'fields': [
                            {
                                'name': 'Title',
                                'slug': 'title',
                                'type': 'text',
                                'required': True,
                                'unique': False,
                                'default': '',
                                'config': {'max_length': 160},
                            }
                        ],
                    }
                ]
            },
        )

        SchemaEngine().apply_snapshot(snapshot)

        old_type.refresh_from_db()
        self.assertFalse(old_type.is_active)

        article = CustomContentType.objects.get(slug='article')
        self.assertTrue(article.is_active)
        self.assertEqual(article.config, {'strict_fields': True})
        title = article.fields.get(slug='title')
        self.assertTrue(title.required)
        self.assertEqual(title.config, {'max_length': 160})

    def test_invalid_snapshot_shape_is_rejected(self):
        snapshot = BuilderSnapshot.objects.create(
            name='Bad snapshot',
            schema={'content_types': 'not-a-list'},
        )

        with self.assertRaises(ValueError):
            SchemaEngine().apply_snapshot(snapshot)
