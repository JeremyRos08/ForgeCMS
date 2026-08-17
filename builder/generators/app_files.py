class AppFilesMixin:
    def _generate_app_package(self):
        app = self.app_name
        return [
            self._write(f'{app}/__init__.py', ''),
            self._write(f'{app}/apps.py', self._build_apps_py()),
            self._write(f'{app}/migrations/__init__.py', ''),
            self._write(f'{app}/models.py', self._build_models_py()),
            self._write(f'{app}/admin.py', self._build_admin_py()),
            self._write(f'{app}/forms.py', self._build_forms_py()),
            self._write(f'{app}/views.py', self._build_views_py()),
            self._write(f'{app}/urls.py', self._build_app_urls_py()),
        ]

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

    def _build_apps_py(self):
        return """from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'content'
"""

    def _build_models_py(self):
        lines = ['from django.db import models', '', '']
        if not self.content_types:
            lines.extend([
                'class PlaceholderContent(models.Model):',
                '    title = models.CharField(max_length=255)',
                '',
                '    def __str__(self):',
                '        return self.title',
            ])
            return '\n'.join(lines) + '\n'

        for ctype in self.content_types:
            lines.append(f"class {ctype['class_name']}(models.Model):")
            if ctype['fields']:
                for field in ctype['fields']:
                    lines.append(f"    {field['field_name']} = {self._field_code(field)}")
            else:
                lines.append('    title = models.CharField(max_length=255)')
            lines.append('    created_at = models.DateTimeField(auto_now_add=True)')
            lines.append('    updated_at = models.DateTimeField(auto_now=True)')
            lines.append('')
            lines.append('    class Meta:')
            lines.append(f"        verbose_name = {ctype['name']!r}")
            lines.append(f"        verbose_name_plural = {(ctype['name'] + 's')!r}")
            lines.append("        ordering = ['-id']")
            lines.append('')
            str_field = self._str_field(ctype)
            lines.append('    def __str__(self):')
            if str_field:
                lines.append(f'        return str(self.{str_field})')
            else:
                lines.append("        return f'Entry #{self.id}'")
            lines.extend(['', ''])
        return '\n'.join(lines).rstrip() + '\n'

    def _build_admin_py(self):
        lines = ['from django.contrib import admin', 'from . import models', '', '']
        if not self.content_types:
            lines.extend([
                '@admin.register(models.PlaceholderContent)',
                'class PlaceholderContentAdmin(admin.ModelAdmin):',
                "    list_display = ('id', 'title')",
                '',
            ])
            return '\n'.join(lines)

        for ctype in self.content_types:
            cls = ctype['class_name']
            list_fields = ['id']
            for field in ctype['fields'][:3]:
                list_fields.append(field['field_name'])
            list_fields.append('updated_at')

            search_fields = [
                f"'{field['field_name']}'"
                for field in ctype['fields']
                if field['type'] in {'text', 'textarea', 'richtext'}
            ]
            if not search_fields:
                search_fields = ["'id'"]

            lines.append(f'@admin.register(models.{cls})')
            lines.append(f'class {cls}Admin(admin.ModelAdmin):')
            lines.append(f"    list_display = ({', '.join(repr(value) for value in list_fields)})")
            lines.append(f"    search_fields = ({', '.join(search_fields)})")
            lines.extend(['', ''])
        return '\n'.join(lines).rstrip() + '\n'

    def _build_forms_py(self):
        lines = ['from django import forms', 'from . import models', '', '']
        if not self.content_types:
            lines.extend([
                'class PlaceholderContentForm(forms.ModelForm):',
                '    class Meta:',
                '        model = models.PlaceholderContent',
                "        fields = '__all__'",
            ])
            return '\n'.join(lines) + '\n'

        for ctype in self.content_types:
            cls = ctype['class_name']
            lines.append(f'class {cls}Form(forms.ModelForm):')
            lines.append('    class Meta:')
            lines.append(f'        model = models.{cls}')
            lines.append("        fields = '__all__'")
            lines.extend(['', ''])
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
            lines.extend([
                f"    '{slug}': {{",
                f"        'label': {label!r},",
                f"        'model': models.{cls},",
                f"        'form': forms.{cls}Form,",
                '    },',
            ])
        lines.extend([
            '}',
            '',
            '',
            'def _cfg(type_slug):',
            '    cfg = CONTENT_MAP.get(type_slug)',
            '    if not cfg:',
            "        raise Http404('Unknown content type')",
            '    return cfg',
            '',
            '',
            'def index(request):',
            "    return render(request, 'content/index.html', {'content_types': CONTENT_MAP})",
            '',
            '',
            'def entry_list(request, type_slug):',
            '    cfg = _cfg(type_slug)',
            "    entries = cfg['model'].objects.all().order_by('-id')",
            "    return render(request, f'content/{type_slug}_list.html', {'cfg': cfg, 'type_slug': type_slug, 'entries': entries})",
            '',
            '',
            'def entry_detail(request, type_slug, pk):',
            '    cfg = _cfg(type_slug)',
            "    entry = get_object_or_404(cfg['model'], pk=pk)",
            '    rows = []',
            '    for field in entry._meta.fields:',
            "        rows.append({'name': field.name, 'value': getattr(entry, field.name)})",
            "    return render(request, f'content/{type_slug}_detail.html', {'cfg': cfg, 'type_slug': type_slug, 'entry': entry, 'rows': rows})",
            '',
            '',
            'def entry_create(request, type_slug):',
            '    cfg = _cfg(type_slug)',
            "    form = cfg['form'](request.POST or None, request.FILES or None)",
            "    if request.method == 'POST' and form.is_valid():",
            '        entry = form.save()',
            "        return redirect('content:entry_detail', type_slug=type_slug, pk=entry.pk)",
            "    return render(request, f'content/{type_slug}_form.html', {'cfg': cfg, 'type_slug': type_slug, 'form': form, 'mode': 'create'})",
            '',
            '',
            'def entry_update(request, type_slug, pk):',
            '    cfg = _cfg(type_slug)',
            "    entry = get_object_or_404(cfg['model'], pk=pk)",
            "    form = cfg['form'](request.POST or None, request.FILES or None, instance=entry)",
            "    if request.method == 'POST' and form.is_valid():",
            '        entry = form.save()',
            "        return redirect('content:entry_detail', type_slug=type_slug, pk=entry.pk)",
            "    return render(request, f'content/{type_slug}_form.html', {'cfg': cfg, 'type_slug': type_slug, 'form': form, 'mode': 'update', 'entry': entry})",
            '',
            '',
            'def entry_delete(request, type_slug, pk):',
            '    cfg = _cfg(type_slug)',
            "    entry = get_object_or_404(cfg['model'], pk=pk)",
            "    if request.method == 'POST':",
            '        entry.delete()',
            "        return redirect('content:entry_list', type_slug=type_slug)",
            "    return render(request, f'content/{type_slug}_confirm_delete.html', {'cfg': cfg, 'type_slug': type_slug, 'entry': entry})",
            '',
        ])
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
