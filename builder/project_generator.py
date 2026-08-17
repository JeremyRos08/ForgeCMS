import keyword
import re
from pathlib import Path

from django.utils.text import slugify


class GeneratedCMSProjectGenerator:
    def __init__(self, schema, output_dir, project_slug='forge_generated_cms', project_name='Forge Generated CMS'):
        self.schema = schema or {}
        self.output_dir = Path(output_dir)
        self.project_name = project_name.strip() or 'Forge Generated CMS'
        self.project_slug = self._safe_module_name(project_slug) or 'forge_generated_cms'
        self.app_name = 'content'
        self.content_types = self._normalize_content_types(self.schema.get('content_types', []))

    def generate(self):
        self._ensure_base()
        created = []
        created.extend(self._generate_root_files())
        created.extend(self._generate_project_package())
        created.extend(self._generate_app_package())
        created.extend(self._generate_templates())
        created.append(self._write('static/css/style.css', self._build_css()))
        return created

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

            class_name = self._to_class_name(type_slug)
            fields = self._normalize_fields(raw.get('fields', []))
            normalized.append(
                {
                    'name': name,
                    'slug': type_slug,
                    'class_name': class_name,
                    'fields': fields,
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

            field_type = str(raw.get('type') or 'text')
            normalized.append(
                {
                    'name': str(raw.get('name') or field_name),
                    'slug': field_slug,
                    'field_name': field_name,
                    'type': field_type,
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

    def _generate_root_files(self):
        files = []
        files.append(self._write('manage.py', self._build_manage_py()))
        files.append(self._write('requirements.txt', self._build_requirements()))
        files.append(self._write('.env.example', self._build_env_example()))
        files.append(self._write('README.md', self._build_readme()))
        return files

    def _generate_project_package(self):
        files = []
        pkg = self.project_slug
        files.append(self._write(f'{pkg}/__init__.py', ''))
        files.append(self._write(f'{pkg}/settings.py', self._build_settings_py()))
        files.append(self._write(f'{pkg}/urls.py', self._build_project_urls_py()))
        files.append(self._write(f'{pkg}/wsgi.py', self._build_wsgi_py()))
        files.append(self._write(f'{pkg}/asgi.py', self._build_asgi_py()))
        return files

    def _generate_app_package(self):
        files = []
        app = self.app_name
        files.append(self._write(f'{app}/__init__.py', ''))
        files.append(self._write(f'{app}/apps.py', self._build_apps_py()))
        files.append(self._write(f'{app}/migrations/__init__.py', ''))
        files.append(self._write(f'{app}/models.py', self._build_models_py()))
        files.append(self._write(f'{app}/admin.py', self._build_admin_py()))
        files.append(self._write(f'{app}/forms.py', self._build_forms_py()))
        files.append(self._write(f'{app}/views.py', self._build_views_py()))
        files.append(self._write(f'{app}/urls.py', self._build_app_urls_py()))
        return files

    def _generate_templates(self):
        files = []
        files.append(self._write('templates/base.html', self._build_base_template()))
        files.append(self._write('templates/content/index.html', self._build_index_template()))
        for ctype in self.content_types:
            slug = ctype['slug']
            files.append(self._write(f'templates/content/{slug}_list.html', self._build_list_template(ctype)))
            files.append(self._write(f'templates/content/{slug}_detail.html', self._build_detail_template(ctype)))
            files.append(self._write(f'templates/content/{slug}_form.html', self._build_form_template(ctype)))
            files.append(
                self._write(
                    f'templates/content/{slug}_confirm_delete.html',
                    self._build_confirm_delete_template(ctype),
                )
            )
        return files

    def _field_code(self, field):
        field_type = field['type']
        required = field['required']
        unique = field['unique']
        default = field['default']

        options = []
        if unique:
            options.append('unique=True')

        if field_type in {'text', 'textarea', 'richtext'}:
            if not required:
                options.append('blank=True')
        elif field_type in {'number', 'date', 'datetime', 'image', 'file', 'relation'}:
            if not required:
                options.append('blank=True')
                options.append('null=True')

        default_code = self._default_code(field_type, default)
        if default_code is not None:
            options.append(f'default={default_code}')

        options_code = ', '.join(options)
        if options_code:
            options_code = ', ' + options_code

        if field_type == 'text':
            return f"models.CharField(max_length=255{options_code})"
        if field_type in {'textarea', 'richtext'}:
            return f"models.TextField({options_code.lstrip(', ')})" if options_code else 'models.TextField()'
        if field_type == 'number':
            return f"models.DecimalField(max_digits=12, decimal_places=2{options_code})"
        if field_type == 'boolean':
            if default_code is None:
                return 'models.BooleanField(default=False)'
            return f'models.BooleanField(default={default_code})'
        if field_type == 'date':
            return f"models.DateField({options_code.lstrip(', ')})" if options_code else 'models.DateField()'
        if field_type == 'datetime':
            return f"models.DateTimeField({options_code.lstrip(', ')})" if options_code else 'models.DateTimeField()'
        if field_type == 'image':
            if options_code:
                return f'models.ImageField(upload_to="uploads/images/"{options_code})'
            return 'models.ImageField(upload_to="uploads/images/")'
        if field_type == 'file':
            if options_code:
                return f'models.FileField(upload_to="uploads/files/"{options_code})'
            return 'models.FileField(upload_to="uploads/files/")'
        if field_type == 'relation':
            if options_code:
                return f'models.ForeignKey("self", on_delete=models.SET_NULL{options_code})'
            return 'models.ForeignKey("self", on_delete=models.SET_NULL)'
        return f"models.CharField(max_length=255{options_code})"

    def _default_code(self, field_type, default_value):
        if default_value in (None, ''):
            return None
        if field_type == 'boolean':
            value = str(default_value).strip().lower()
            return 'True' if value in {'1', 'true', 'yes', 'on'} else 'False'
        if field_type == 'number':
            return repr(str(default_value))
        if field_type in {'relation', 'image', 'file'}:
            return None
        return repr(str(default_value))

    def _str_field(self, ctype):
        for field in ctype['fields']:
            if field['type'] in {'text', 'textarea', 'richtext'}:
                return field['field_name']
        if ctype['fields']:
            return ctype['fields'][0]['field_name']
        return None

    def _build_manage_py(self):
        return f"""#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{self.project_slug}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it is installed and available on your "
            "PYTHONPATH environment variable? Did you forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
"""

    def _build_requirements(self):
        return "Django>=5.0,<6.0\nPillow>=10.0,<12.0\n"

    def _build_env_example(self):
        return "SECRET_KEY=change-me\nDEBUG=True\nALLOWED_HOSTS=127.0.0.1,localhost\n"

    def _build_readme(self):
        type_lines = '\n'.join(
            [f"- `{ctype['name']}` (`{ctype['slug']}`) with {len(ctype['fields'])} fields" for ctype in self.content_types]
        )
        if not type_lines:
            type_lines = '- No content type found in source schema.'
        return f"""# {self.project_name}

Generated from ForgeCMS Builder schema.

## Included Content Types
{type_lines}

## Run
```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
"""

    def _build_settings_py(self):
        return f"""from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'generated-cms-dev-secret')
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    '{self.app_name}',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{self.project_slug}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{self.project_slug}.wsgi.application'
ASGI_APPLICATION = '{self.project_slug}.asgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""

    def _build_project_urls_py(self):
        return """from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('content.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

    def _build_wsgi_py(self):
        return f"""import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{self.project_slug}.settings')
application = get_wsgi_application()
"""

    def _build_asgi_py(self):
        return f"""import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{self.project_slug}.settings')
application = get_asgi_application()
"""

    def _build_apps_py(self):
        return """from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
"""

    def _build_models_py(self):
        lines = ["from django.db import models", "", ""]
        if not self.content_types:
            lines.append("class PlaceholderContent(models.Model):")
            lines.append("    title = models.CharField(max_length=255)")
            lines.append("")
            lines.append("    def __str__(self):")
            lines.append("        return self.title")
            return '\n'.join(lines) + '\n'

        for ctype in self.content_types:
            lines.append(f"class {ctype['class_name']}(models.Model):")
            if ctype['fields']:
                for field in ctype['fields']:
                    lines.append(f"    {field['field_name']} = {self._field_code(field)}")
            else:
                lines.append("    title = models.CharField(max_length=255)")
            lines.append("    created_at = models.DateTimeField(auto_now_add=True)")
            lines.append("    updated_at = models.DateTimeField(auto_now=True)")
            lines.append("")
            lines.append("    class Meta:")
            lines.append(f"        verbose_name = '{ctype['name']}'")
            lines.append(f"        verbose_name_plural = '{ctype['name']}s'")
            lines.append("        ordering = ['-id']")
            lines.append("")
            str_field = self._str_field(ctype)
            lines.append("    def __str__(self):")
            if str_field:
                lines.append(f"        return str(self.{str_field})")
            else:
                lines.append("        return f'Entry #{self.id}'")
            lines.append("")
            lines.append("")
        return '\n'.join(lines).rstrip() + '\n'

    def _build_admin_py(self):
        imports = ['from django.contrib import admin', 'from . import models', '', '']
        lines = imports
        if not self.content_types:
            lines.append('@admin.register(models.PlaceholderContent)')
            lines.append('class PlaceholderContentAdmin(admin.ModelAdmin):')
            lines.append("    list_display = ('id', 'title', 'created_at')")
            lines.append("")
            return '\n'.join(lines)

        for ctype in self.content_types:
            cls = ctype['class_name']
            list_fields = ['id']
            for field in ctype['fields'][:3]:
                list_fields.append(field['field_name'])
            list_fields.append('updated_at')

            search_fields = [f"'{f['field_name']}'" for f in ctype['fields'] if f['type'] in {'text', 'textarea', 'richtext'}]
            if not search_fields:
                search_fields = ["'id'"]

            lines.append(f"@admin.register(models.{cls})")
            lines.append(f'class {cls}Admin(admin.ModelAdmin):')
            lines.append(f"    list_display = ({', '.join(repr(v) for v in list_fields)})")
            lines.append(f"    search_fields = ({', '.join(search_fields)})")
            lines.append("")
            lines.append("")
        return '\n'.join(lines).rstrip() + '\n'

    def _build_forms_py(self):
        lines = ['from django import forms', 'from . import models', '', '']
        if not self.content_types:
            lines.append('class PlaceholderContentForm(forms.ModelForm):')
            lines.append('    class Meta:')
            lines.append('        model = models.PlaceholderContent')
            lines.append("        fields = '__all__'")
            return '\n'.join(lines) + '\n'

        for ctype in self.content_types:
            cls = ctype['class_name']
            lines.append(f'class {cls}Form(forms.ModelForm):')
            lines.append('    class Meta:')
            lines.append(f'        model = models.{cls}')
            lines.append("        fields = '__all__'")
            lines.append("")
            lines.append("")
        return '\n'.join(lines).rstrip() + '\n'

    def _build_views_py(self):
        lines = [
            'from django.http import Http404',
            'from django.shortcuts import get_object_or_404, redirect, render',
            '',
            'from . import forms, models',
            '',
            '',
            'CONTENT_MAP = {',
        ]
        for ctype in self.content_types:
            slug = ctype['slug']
            cls = ctype['class_name']
            label = ctype['name']
            lines.append(f"    '{slug}': {{")
            lines.append(f"        'label': {label!r},")
            lines.append(f"        'model': models.{cls},")
            lines.append(f"        'form': forms.{cls}Form,")
            lines.append("    },")
        lines.append('}')
        lines.append('')
        lines.append('')
        lines.append('def _cfg(type_slug):')
        lines.append('    cfg = CONTENT_MAP.get(type_slug)')
        lines.append('    if not cfg:')
        lines.append("        raise Http404('Unknown content type')")
        lines.append('    return cfg')
        lines.append('')
        lines.append('')
        lines.append('def index(request):')
        lines.append("    return render(request, 'content/index.html', {'content_types': CONTENT_MAP})")
        lines.append('')
        lines.append('')
        lines.append('def entry_list(request, type_slug):')
        lines.append('    cfg = _cfg(type_slug)')
        lines.append("    entries = cfg['model'].objects.all().order_by('-id')")
        lines.append("    return render(request, f'content/{type_slug}_list.html', {'cfg': cfg, 'type_slug': type_slug, 'entries': entries})")
        lines.append('')
        lines.append('')
        lines.append('def entry_detail(request, type_slug, pk):')
        lines.append('    cfg = _cfg(type_slug)')
        lines.append("    entry = get_object_or_404(cfg['model'], pk=pk)")
        lines.append('    rows = []')
        lines.append('    for field in entry._meta.fields:')
        lines.append("        rows.append({'name': field.name, 'value': getattr(entry, field.name)})")
        lines.append("    return render(request, f'content/{type_slug}_detail.html', {'cfg': cfg, 'type_slug': type_slug, 'entry': entry, 'rows': rows})")
        lines.append('')
        lines.append('')
        lines.append('def entry_create(request, type_slug):')
        lines.append('    cfg = _cfg(type_slug)')
        lines.append("    form = cfg['form'](request.POST or None, request.FILES or None)")
        lines.append('    if request.method == \'POST\' and form.is_valid():')
        lines.append('        entry = form.save()')
        lines.append("        return redirect('content:entry_detail', type_slug=type_slug, pk=entry.pk)")
        lines.append("    return render(request, f'content/{type_slug}_form.html', {'cfg': cfg, 'type_slug': type_slug, 'form': form, 'mode': 'create'})")
        lines.append('')
        lines.append('')
        lines.append('def entry_update(request, type_slug, pk):')
        lines.append('    cfg = _cfg(type_slug)')
        lines.append("    entry = get_object_or_404(cfg['model'], pk=pk)")
        lines.append("    form = cfg['form'](request.POST or None, request.FILES or None, instance=entry)")
        lines.append('    if request.method == \'POST\' and form.is_valid():')
        lines.append('        entry = form.save()')
        lines.append("        return redirect('content:entry_detail', type_slug=type_slug, pk=entry.pk)")
        lines.append("    return render(request, f'content/{type_slug}_form.html', {'cfg': cfg, 'type_slug': type_slug, 'form': form, 'mode': 'update', 'entry': entry})")
        lines.append('')
        lines.append('')
        lines.append('def entry_delete(request, type_slug, pk):')
        lines.append('    cfg = _cfg(type_slug)')
        lines.append("    entry = get_object_or_404(cfg['model'], pk=pk)")
        lines.append("    if request.method == 'POST':")
        lines.append('        entry.delete()')
        lines.append("        return redirect('content:entry_list', type_slug=type_slug)")
        lines.append("    return render(request, f'content/{type_slug}_confirm_delete.html', {'cfg': cfg, 'type_slug': type_slug, 'entry': entry})")
        lines.append('')
        return '\n'.join(lines)

    def _build_app_urls_py(self):
        return """from django.urls import path

from . import views

app_name = 'content'

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:type_slug>/', views.entry_list, name='entry_list'),
    path('<slug:type_slug>/new/', views.entry_create, name='entry_create'),
    path('<slug:type_slug>/<int:pk>/', views.entry_detail, name='entry_detail'),
    path('<slug:type_slug>/<int:pk>/edit/', views.entry_update, name='entry_update'),
    path('<slug:type_slug>/<int:pk>/delete/', views.entry_delete, name='entry_delete'),
]
"""

    def _build_base_template(self):
        return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{% block title %}}{self.project_name}{{% endblock %}}</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <header class="topbar">
    <a class="brand" href="/"> {self.project_name} </a>
    <nav>
      <a href="/">Accueil</a>
      <a href="/admin/">Admin</a>
    </nav>
  </header>
  <main class="container">
    {{% block content %}}{{% endblock %}}
  </main>
</body>
</html>
"""

    def _build_index_template(self):
        return """{% extends 'base.html' %}
{% block title %}Accueil{% endblock %}
{% block content %}
<section class="panel">
  <h1>Content Types</h1>
  <p>Generated from ForgeCMS Builder.</p>
  <ul class="stack">
    {% for slug, cfg in content_types.items %}
      <li class="panel">
        <strong>{{ cfg.label }}</strong><br>
        <a class="button" href="{% url 'content:entry_list' type_slug=slug %}">Open {{ cfg.label }}</a>
      </li>
    {% empty %}
      <li class="panel">No content type in schema.</li>
    {% endfor %}
  </ul>
</section>
{% endblock %}
"""

    def _build_list_template(self, ctype):
        return """{% extends 'base.html' %}
{% block title %}{{ cfg.label }}{% endblock %}
{% block content %}
<section class="panel">
  <h1>{{ cfg.label }}</h1>
  <p><a class="button" href="{% url 'content:entry_create' type_slug=type_slug %}">New entry</a></p>
  <ul class="stack">
    {% for entry in entries %}
      <li class="panel">
        <a href="{% url 'content:entry_detail' type_slug=type_slug pk=entry.pk %}">Entry #{{ entry.pk }}</a>
      </li>
    {% empty %}
      <li class="panel">No entries yet.</li>
    {% endfor %}
  </ul>
</section>
{% endblock %}
"""

    def _build_detail_template(self, ctype):
        return """{% extends 'base.html' %}
{% block title %}{{ cfg.label }} #{{ entry.pk }}{% endblock %}
{% block content %}
<section class="panel">
  <h1>{{ cfg.label }} #{{ entry.pk }}</h1>
  <ul class="stack">
    {% for row in rows %}
      <li class="panel"><strong>{{ row.name }}</strong>: {{ row.value|default:'-' }}</li>
    {% endfor %}
  </ul>
  <p class="actions">
    <a class="button ghost" href="{% url 'content:entry_update' type_slug=type_slug pk=entry.pk %}">Edit</a>
    <a class="button ghost" href="{% url 'content:entry_delete' type_slug=type_slug pk=entry.pk %}">Delete</a>
    <a class="button" href="{% url 'content:entry_list' type_slug=type_slug %}">Back</a>
  </p>
</section>
{% endblock %}
"""

    def _build_form_template(self, ctype):
        return """{% extends 'base.html' %}
{% block title %}{{ cfg.label }}{% endblock %}
{% block content %}
<section class="panel">
  <h1>{{ cfg.label }} - {% if mode == 'create' %}Create{% else %}Update{% endif %}</h1>
  <form method="post" enctype="multipart/form-data" class="stack">
    {% csrf_token %}
    {{ form.as_p }}
    <button class="button" type="submit">Save</button>
    <a class="button ghost" href="{% url 'content:entry_list' type_slug=type_slug %}">Cancel</a>
  </form>
</section>
{% endblock %}
"""

    def _build_confirm_delete_template(self, ctype):
        return """{% extends 'base.html' %}
{% block title %}Delete {{ cfg.label }}{% endblock %}
{% block content %}
<section class="panel">
  <h1>Delete {{ cfg.label }} #{{ entry.pk }}</h1>
  <form method="post">
    {% csrf_token %}
    <p>This action is irreversible.</p>
    <button class="button" type="submit">Confirm delete</button>
    <a class="button ghost" href="{% url 'content:entry_detail' type_slug=type_slug pk=entry.pk %}">Cancel</a>
  </form>
</section>
{% endblock %}
"""

    def _build_css(self):
        return """:root {
  --bg: #0b1324;
  --panel: #13203a;
  --text: #e6edf7;
  --muted: #9bb0cb;
  --accent: #7dd3fc;
  --border: rgba(255, 255, 255, .14);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: "Segoe UI", Tahoma, sans-serif;
  background: radial-gradient(circle at top, #1e3a8a, var(--bg));
  color: var(--text);
}
a { color: var(--accent); text-decoration: none; }
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border);
}
.brand { color: var(--text); font-weight: 700; }
.container { width: min(1080px, calc(100% - 24px)); margin: 28px auto; }
.panel {
  padding: 18px;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: rgba(8, 15, 30, .45);
}
.stack { display: grid; gap: 10px; padding: 0; list-style: none; }
.button {
  display: inline-block;
  background: var(--accent);
  color: #04233a;
  padding: 10px 14px;
  border-radius: 10px;
  font-weight: 700;
}
.button.ghost {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
}
"""
