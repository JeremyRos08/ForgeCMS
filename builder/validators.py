from decimal import Decimal, InvalidOperation

from django.utils.dateparse import parse_date, parse_datetime


EMPTY_VALUES = (None, '')


def _as_decimal(value):
    if isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return number if number.is_finite() else None


def _relation_ids(value, multiple=False):
    values = value if multiple and isinstance(value, (list, tuple)) else [value]
    if multiple and not isinstance(value, (list, tuple)):
        return None

    relation_ids = []
    for item in values:
        if isinstance(item, bool):
            return None
        try:
            relation_id = int(item)
        except (TypeError, ValueError):
            return None
        if relation_id <= 0:
            return None
        relation_ids.append(relation_id)
    return relation_ids


def validate_entry_data(content_type, data, instance=None):
    """Validate JSON data against the fields configured for a content type.

    Returns a ``{field_slug: message}`` dictionary. An empty dictionary means
    the entry is valid. The function is intentionally independent from forms
    so it can be reused by the admin, APIs, commands and plugins.
    """
    if not isinstance(data, dict):
        return {'_schema': 'Les données doivent être un objet JSON.'}

    errors = {}
    fields = list(content_type.fields.all())
    known_slugs = {field.slug for field in fields}

    if isinstance(content_type.config, dict) and content_type.config.get('strict_fields'):
        unknown = sorted(set(data) - known_slugs)
        if unknown:
            errors['_schema'] = f"Champs inconnus : {', '.join(unknown)}."

    for field in fields:
        value = data.get(field.slug)
        config = field.config if isinstance(field.config, dict) else {}

        is_empty = value in EMPTY_VALUES or (config.get('multiple') and value == [])
        if is_empty:
            if field.required:
                errors[field.slug] = 'Champ obligatoire.'
            continue

        if field.field_type in {'text', 'textarea', 'richtext'}:
            if not isinstance(value, str):
                errors[field.slug] = 'La valeur doit être du texte.'
                continue
            min_length = config.get('min_length')
            max_length = config.get('max_length')
            if isinstance(min_length, int) and len(value) < min_length:
                errors[field.slug] = f'Longueur minimale : {min_length} caractères.'
                continue
            if isinstance(max_length, int) and len(value) > max_length:
                errors[field.slug] = f'Longueur maximale : {max_length} caractères.'
                continue

        elif field.field_type == 'number':
            number = _as_decimal(value)
            if number is None:
                errors[field.slug] = 'La valeur doit être un nombre valide.'
                continue

            minimum = _as_decimal(config.get('min')) if config.get('min') is not None else None
            maximum = _as_decimal(config.get('max')) if config.get('max') is not None else None
            if minimum is not None and number < minimum:
                errors[field.slug] = f'La valeur minimale est {minimum}.'
                continue
            if maximum is not None and number > maximum:
                errors[field.slug] = f'La valeur maximale est {maximum}.'
                continue

        elif field.field_type == 'boolean':
            if not isinstance(value, bool):
                errors[field.slug] = 'La valeur doit être un booléen.'
                continue

        elif field.field_type == 'date':
            if not isinstance(value, str) or parse_date(value) is None:
                errors[field.slug] = 'La date doit être au format ISO AAAA-MM-JJ.'
                continue

        elif field.field_type == 'datetime':
            if not isinstance(value, str) or parse_datetime(value) is None:
                errors[field.slug] = 'La date/heure doit être au format ISO.'
                continue

        elif field.field_type in {'image', 'file'}:
            if not isinstance(value, str):
                errors[field.slug] = 'La valeur doit être un chemin ou une URL.'
                continue

        elif field.field_type == 'relation':
            relation_ids = _relation_ids(value, multiple=bool(config.get('multiple')))
            if relation_ids is None:
                errors[field.slug] = 'La relation doit contenir un identifiant valide.'
                continue

            # Import local pour éviter une dépendance circulaire models -> validators.
            from .models import CustomEntry

            related_entries = CustomEntry.objects.filter(pk__in=relation_ids)
            target_slug = config.get('target_content_type')
            if target_slug:
                related_entries = related_entries.filter(content_type__slug=target_slug)

            if related_entries.count() != len(set(relation_ids)):
                errors[field.slug] = 'Une ou plusieurs entrées liées sont introuvables ou incompatibles.'
                continue

        choices = config.get('choices')
        if isinstance(choices, list) and choices and value not in choices:
            errors[field.slug] = 'La valeur ne fait pas partie des choix autorisés.'
            continue

        if field.unique:
            lookup = {f'data__{field.slug}': value}
            queryset = content_type.entries.filter(**lookup)
            if instance is not None and instance.pk:
                queryset = queryset.exclude(pk=instance.pk)
            if queryset.exists():
                errors[field.slug] = 'Cette valeur doit être unique.'

    return errors
