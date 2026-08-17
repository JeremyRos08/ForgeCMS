from django.db import transaction
from django.utils import timezone

from .field_types import FIELD_TYPES
from .models import BuilderSnapshot, CustomContentType, CustomField

VALID_FIELD_TYPES = {key for key, _label in FIELD_TYPES}


class SchemaEngine:
    def export_schema(self):
        content_types = (
            CustomContentType.objects.filter(is_active=True)
            .prefetch_related('fields')
            .order_by('name')
        )
        return {
            'project': {
                'name': 'ForgeCMS Generated Project',
                'version': '0.1.0',
            },
            'content_types': [ctype.to_schema() for ctype in content_types],
        }

    def create_snapshot(self, user=None, note='', is_auto=False):
        schema = self.export_schema()
        timestamp = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
        snapshot = BuilderSnapshot.objects.create(
            name=f'Snapshot {timestamp}',
            note=note or '',
            schema=schema,
            is_auto=is_auto,
            created_by=user if getattr(user, 'is_authenticated', False) else None,
        )
        return snapshot

    @transaction.atomic
    def apply_snapshot(self, snapshot):
        content_types = snapshot.schema.get('content_types', [])
        if not isinstance(content_types, list):
            raise ValueError('Snapshot invalide: content_types doit etre une liste.')

        seen_type_slugs = set()

        for ctype_data in content_types:
            slug = ctype_data.get('slug')
            if not slug:
                raise ValueError('Snapshot invalide: un type n a pas de slug.')
            seen_type_slugs.add(slug)

            ctype, _created = CustomContentType.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': ctype_data.get('name', slug),
                    'description': ctype_data.get('description', ''),
                    'config': ctype_data.get('config') if isinstance(ctype_data.get('config'), dict) else {},
                    'is_active': True,
                },
            )

            fields = ctype_data.get('fields', [])
            if not isinstance(fields, list):
                raise ValueError(f'Snapshot invalide: fields doit etre une liste pour {slug}.')

            seen_field_slugs = set()
            for order_index, field_data in enumerate(fields):
                field_slug = field_data.get('slug')
                if not field_slug:
                    raise ValueError(f'Snapshot invalide: un champ de {slug} n a pas de slug.')
                seen_field_slugs.add(field_slug)
                field_type = field_data.get('type', 'text')
                if field_type not in VALID_FIELD_TYPES:
                    field_type = 'text'

                CustomField.objects.update_or_create(
                    content_type=ctype,
                    slug=field_slug,
                    defaults={
                        'name': field_data.get('name', field_slug),
                        'field_type': field_type,
                        'required': bool(field_data.get('required', False)),
                        'unique': bool(field_data.get('unique', False)),
                        'default_value': str(field_data.get('default', '')) if field_data.get('default') is not None else '',
                        'config': field_data.get('config') if isinstance(field_data.get('config'), dict) else {},
                        'order': order_index,
                    },
                )

            ctype.fields.exclude(slug__in=seen_field_slugs).delete()

        CustomContentType.objects.exclude(slug__in=seen_type_slugs).update(is_active=False)
