class ProjectFilesMixin:
    def _generate_root_files(self):
        return [
            self._write('manage.py', self._build_manage_py()),
            self._write('requirements.txt', self._build_requirements()),
            self._write('.env.example', self._build_env_example()),
            self._write('README.md', self._build_readme()),
        ]

    def _generate_project_package(self):
        pkg = self.project_slug
        return [
            self._write(f'{pkg}/__init__.py', ''),
            self._write(f'{pkg}/settings.py', self._build_settings_py()),
            self._write(f'{pkg}/urls.py', self._build_project_urls_py()),
            self._write(f'{pkg}/wsgi.py', self._build_wsgi_py()),
            self._write(f'{pkg}/asgi.py', self._build_asgi_py()),
        ]

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
