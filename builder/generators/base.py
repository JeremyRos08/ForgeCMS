import keyword
import re
from pathlib import Path

from django.utils.text import slugify


class GeneratorBase:
    """Shared filesystem and schema-normalization helpers for generators."""

    def __init__(self, schema, output_dir, project_slug='forge_generated_cms', project_name='Forge Generated CMS'):
        self.schema = schema or {}
        self.output_dir = Path(output_dir)
        self.project_name = project_name.strip() or 'Forge Generated CMS'
        self.project_slug = self._safe_module_name(project_slug) or 'forge_generated_cms'
        self.app_name = 'content'
        self.content_types = self._normalize_content_types(self.schema.get('content_types', []))

    def _ensure_base(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _write(self, rel_path, content):
        path = self.output_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return path

    def _normalize_content_types(self, content_types):
        normalized = []
        seen_type_slugs = set()

        for index, raw in enumerate(content_types, start=1):
            name = str(raw.get('name') or f'Content Type {index}').strip()
            type_slug = slugify(raw.get('slug') or name) or f'content_type_{index}'
            if type_slug in seen_type_slugs:
                type_slug = f'{type_slug}_{index}'
            seen_type_slugs.add(type_slug)

            normalized.append(
                {
                    'name': name,
                    'slug': type_slug,
                    'class_name': self._to_class_name(type_slug),
                    'fields': self._normalize_fields(raw.get('fields', [])),
                }
            )
        return normalized

    def _normalize_fields(self, fields):
        normalized = []
        seen_names = set()

        for index, raw in enumerate(fields, start=1):
            field_slug = slugify(raw.get('slug') or raw.get('name') or f'field-{index}') or f'field_{index}'
            field_name = self._safe_field_name(field_slug)
            if field_name in seen_names:
                field_name = f'{field_name}_{index}'
            seen_names.add(field_name)

            normalized.append(
                {
                    'name': str(raw.get('name') or field_name),
                    'slug': field_slug,
                    'field_name': field_name,
                    'type': str(raw.get('type') or 'text'),
                    'required': bool(raw.get('required', False)),
                    'unique': bool(raw.get('unique', False)),
                    'default': raw.get('default', ''),
                }
            )
        return normalized

    def _safe_module_name(self, value):
        clean = re.sub(r'[^a-zA-Z0-9_]+', '_', str(value or '').strip().lower())
        clean = re.sub(r'_+', '_', clean).strip('_')
        if not clean:
            clean = 'generated_project'
        if clean[0].isdigit():
            clean = f'proj_{clean}'
        if keyword.iskeyword(clean):
            clean = f'{clean}_app'
        return clean

    def _safe_field_name(self, value):
        clean = self._safe_module_name(value)
        reserved = {'type', 'class', 'def', 'from', 'import', 'pass', 'return'}
        if clean in reserved:
            clean = f'{clean}_field'
        return clean

    def _to_class_name(self, slug):
        parts = re.split(r'[^a-zA-Z0-9]+', slug)
        name = ''.join(part.capitalize() for part in parts if part)
        if not name:
            name = 'GeneratedModel'
        if name[0].isdigit():
            name = f'Model{name}'
        return name
