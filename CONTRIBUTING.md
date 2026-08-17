# Contribuer à ForgeCMS

Merci de vouloir participer à ForgeCMS.

ForgeCMS est un CMS Django modulaire en cours de construction. Les contributions sont bienvenues : corrections de bugs, documentation, tests, ergonomie, modules, thèmes, API et améliorations du builder.

## Démarrage rapide

1. Forkez le dépôt.
2. Clonez votre fork.
3. Créez une branche dédiée depuis `main`.
4. Installez le projet dans un environnement virtuel.
5. Faites une modification ciblée et testable.
6. Ouvrez une Pull Request vers `main`.

```powershell
git clone https://github.com/<votre-compte>/ForgeCMS.git
cd ForgeCMS
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Branches

Utilisez de préférence un nom explicite :

- `feat/nom-fonctionnalite`
- `fix/nom-correctif`
- `docs/nom-documentation`
- `refactor/nom-refactor`
- `test/nom-tests`

Ne développez pas directement sur `main` dans votre fork si vous prévoyez plusieurs contributions en parallèle.

## Pull Requests

Une bonne PR doit :

- traiter un sujet principal ;
- expliquer le problème et la solution ;
- indiquer comment tester le changement ;
- signaler les migrations Django éventuelles ;
- ne pas inclure de secrets, de `.env`, de base SQLite locale ou de fichiers générés inutiles ;
- rester compatible avec l'architecture modulaire du projet.

Les grosses évolutions d'architecture doivent idéalement commencer par une issue afin d'éviter plusieurs implémentations incompatibles.

## Qualité minimale

Avant d'ouvrir une PR :

```powershell
python manage.py check
python manage.py test
```

Si votre modification ajoute un comportement important, ajoutez ou mettez à jour les tests correspondants lorsque c'est possible.

## Django et migrations

Si vous modifiez des modèles :

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py check
python manage.py test
```

Les migrations nécessaires au fonctionnement de la contribution doivent être incluses dans la PR.

## Modules et extensibilité

ForgeCMS vise une architecture durable et modulaire. Une contribution ne doit pas coupler inutilement le cœur du CMS à un module optionnel.

Préférez :

- des interfaces claires ;
- des responsabilités séparées ;
- des dépendances explicites ;
- des composants réutilisables ;
- une compatibilité ascendante raisonnable.

## Issues

Utilisez les modèles GitHub pour signaler un bug ou proposer une fonctionnalité. Avant d'ouvrir une nouvelle issue, vérifiez rapidement qu'elle n'existe pas déjà.

## Communication

Les désaccords techniques sont normaux. Discutez du code, de l'architecture et des compromis sans attaques personnelles. Les mainteneurs peuvent demander des changements avant fusion afin de préserver la cohérence du projet.
