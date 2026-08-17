class TemplateFilesMixin:
    def _generate_templates(self):
        files = [
            self._write('templates/base.html', self._build_base_template()),
            self._write('templates/content/index.html', self._build_index_template()),
        ]
        for ctype in self.content_types:
            slug = ctype['slug']
            files.extend([
                self._write(f'templates/content/{slug}_list.html', self._build_list_template(ctype)),
                self._write(f'templates/content/{slug}_detail.html', self._build_detail_template(ctype)),
                self._write(f'templates/content/{slug}_form.html', self._build_form_template(ctype)),
                self._write(
                    f'templates/content/{slug}_confirm_delete.html',
                    self._build_confirm_delete_template(ctype),
                ),
            ])
        return files

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
