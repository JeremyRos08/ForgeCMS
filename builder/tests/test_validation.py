from django.core.exceptions import ValidationError
from django.test import TestCase

from builder.models import CustomContentType, CustomEntry, CustomField
from builder.validators import validate_entry_data


class BuilderEntryValidationTests(TestCase):
    def setUp(self):
        self.article = CustomContentType.objects.create(name='Article', slug='article')

    def add_field(self, slug, field_type='text', **kwargs):
        return CustomField.objects.create(
            content_type=self.article,
            name=slug.replace('_', ' ').title(),
            slug=slug,
            field_type=field_type,
            **kwargs,
        )

    def test_required_field_is_enforced(self):
        self.add_field('title', required=True)
        errors = validate_entry_data(self.article, {})
        self.assertEqual(errors['title'], 'Champ obligatoire.')

    def test_number_min_and_max_are_enforced(self):
        self.add_field('price', field_type='number', config={'min': 1, 'max': 100})

        self.assertIn('price', validate_entry_data(self.article, {'price': 'abc'}))
        self.assertIn('price', validate_entry_data(self.article, {'price': 0}))
        self.assertIn('price', validate_entry_data(self.article, {'price': 101}))
        self.assertEqual(validate_entry_data(self.article, {'price': '49.90'}), {})

    def test_boolean_and_date_are_type_checked(self):
        self.add_field('featured', field_type='boolean')
        self.add_field('published_on', field_type='date')

        errors = validate_entry_data(
            self.article,
            {'featured': 'true', 'published_on': '17/08/2026'},
        )
        self.assertIn('featured', errors)
        self.assertIn('published_on', errors)

        self.assertEqual(
            validate_entry_data(
                self.article,
                {'featured': True, 'published_on': '2026-08-17'},
            ),
            {},
        )

    def test_text_length_and_choices_are_enforced(self):
        self.add_field(
            'status',
            config={'min_length': 3, 'max_length': 10, 'choices': ['draft', 'published']},
        )

        self.assertIn('status', validate_entry_data(self.article, {'status': 'x'}))
        self.assertIn('status', validate_entry_data(self.article, {'status': 'archived'}))
        self.assertEqual(validate_entry_data(self.article, {'status': 'draft'}), {})

    def test_unique_json_field_is_enforced(self):
        self.add_field('reference', unique=True)
        CustomEntry.objects.create(content_type=self.article, data={'reference': 'ABC-001'})

        duplicate = CustomEntry(content_type=self.article, data={'reference': 'ABC-001'})
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

        other = CustomEntry(content_type=self.article, data={'reference': 'ABC-002'})
        other.full_clean()

    def test_relation_can_target_another_content_type(self):
        category = CustomContentType.objects.create(name='Category', slug='category')
        target = CustomEntry.objects.create(content_type=category, data={})
        self.add_field(
            'category',
            field_type='relation',
            config={'target_content_type': 'category'},
        )

        self.assertEqual(validate_entry_data(self.article, {'category': target.pk}), {})
        self.assertIn('category', validate_entry_data(self.article, {'category': 999999}))

    def test_multiple_relation_is_supported(self):
        category = CustomContentType.objects.create(name='Category', slug='category')
        first = CustomEntry.objects.create(content_type=category, data={})
        second = CustomEntry.objects.create(content_type=category, data={})
        self.add_field(
            'categories',
            field_type='relation',
            config={'target_content_type': 'category', 'multiple': True},
        )

        self.assertEqual(
            validate_entry_data(self.article, {'categories': [first.pk, second.pk]}),
            {},
        )
        self.assertIn('categories', validate_entry_data(self.article, {'categories': first.pk}))

    def test_strict_fields_can_reject_unknown_keys(self):
        self.article.config = {'strict_fields': True}
        self.article.save(update_fields=['config'])
        self.add_field('title')

        errors = validate_entry_data(self.article, {'title': 'OK', 'typo': 'bad'})
        self.assertIn('_schema', errors)

    def test_save_runs_full_validation(self):
        self.add_field('title', required=True)
        entry = CustomEntry(content_type=self.article, data={})

        with self.assertRaises(ValidationError):
            entry.save()
