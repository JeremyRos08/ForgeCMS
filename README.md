# ForgeCMS V0

ForgeCMS V0 est une base de CMS Django conçue pour évoluer vers une **CMS Factory** : d’abord un CMS modulaire propre, puis un générateur de CMS personnalisés.

## Ce que contient cette V0

- Administration Django
- Pages CMS²
- Blog/articles/catégories
- Bibliothèque média
- Menus
- Registre de modules
- Builder de types de contenu personnalisés
- Entrées stockées en JSON pour prototypage rapide
- Moteur d’export de schéma
- Début de générateur de code via Jinja2
- Thème HTML/CSS minimal
- Configuration VSCode
- Commande de démo `seed_demo`

Ce n’est pas encore un clone de WordPress/Joomla/Drupal. C’est la fondation pour construire ton propre moteur, puis le transformer en application capable de générer d’autres CMS.

---

## Installation Windows / VSCode

Dans PowerShell :

```powershell
cd chemin\vers\ForgeCMS_V0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Puis ouvre :

```txt
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/builder/
```

---

## Structure

```txt
ForgeCMS_V0/
├── manage.py
├── requirements.txt
├── config/
├── core/
├── accounts/
├── pages/
├── blog/
├── media_library/
├── menus/
├── modules/
├── builder/
├── themes/
├── templates/
└── static/
```

---

## Roadmap courte

1. Stabiliser le CMS de base
2. Ajouter des champs personnalisés plus riches
3. Générer automatiquement des CRUD
4. Ajouter une API REST
5. Ajouter un canvas drag & drop pour les entités/champs
6. Exporter un CMS autonome avec Docker


---

## Generer un CMS autonome

Le Builder peut maintenant generer un projet Django autonome depuis le schema courant.

```powershell
python manage.py generate_cms --output generated/my_cms --project-name "My CMS" --project-slug my_cms
```

Puis dans le projet genere:

```powershell
cd generated\my_cms
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
