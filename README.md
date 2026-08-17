# ForgeCMS V0

ForgeCMS V0 est une base de CMS Django conçue pour évoluer vers une **CMS Factory** : d’abord un CMS modulaire propre, puis un générateur de CMS personnalisés.

> Le projet est ouvert aux contributions. Bugs, idées, documentation, modules, thèmes, tests et améliorations du builder sont les bienvenus.

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

Ce n’est pas encore un clone de WordPress/Joomla/Drupal. C’est la fondation pour construire un moteur CMS modulaire, puis le transformer en application capable de générer d’autres CMS.

---

## Installation Windows / VSCode

Dans PowerShell :

```powershell
cd chemin\vers\ForgeCMS
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

## Contribuer

ForgeCMS est public et accepte les contributions par Pull Request.

Le workflow recommandé :

1. Forker `JeremyRos08/ForgeCMS`.
2. Créer une branche depuis `main` (`feat/...`, `fix/...`, `docs/...`).
3. Développer et tester localement.
4. Vérifier :

```powershell
python manage.py check
python manage.py test
```

5. Ouvrir une Pull Request vers `main`.

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) avant une contribution importante et [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) pour les règles de participation.

Pour une vulnérabilité ou un problème sensible, consultez [SECURITY.md](SECURITY.md) et évitez de publier les détails exploitables dans une issue publique.

Les Pull Requests sont contrôlées automatiquement par GitHub Actions.

---

## Structure

```txt
ForgeCMS/
├── manage.py
├── requirements.txt
├── config/
├── core/
├── accounts/
├── pages/
├── blog/
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

## Générer un CMS autonome

Le Builder peut maintenant générer un projet Django autonome depuis le schéma courant.

```powershell
python manage.py generate_cms --output generated/my_cms --project-name "My CMS" --project-slug my_cms
```

Puis dans le projet généré :

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
