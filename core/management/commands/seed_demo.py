from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from core.models import SiteSetting
from pages.models import Page
from blog.models import Category, Article
from modules.models import InstalledModule
from builder.models import CustomContentType, CustomField, CustomEntry


class Command(BaseCommand):
    help = 'Ajoute des données de démonstration ForgeCMS.'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()

        SiteSetting.objects.get_or_create(
            id=1,
            defaults={
                'site_name': 'ForgeCMS',
                'tagline': 'CMS modulaire pensé pour créer des CMS',
            },
        )

        for name, label, desc in [
            ('pages', 'Pages', 'Gestion des pages statiques'),
            ('blog', 'Blog', 'Articles et catégories'),
            ('media_library', 'Médias', 'Bibliothèque de fichiers'),
            ('menus', 'Menus', 'Navigation du site'),
            ('builder', 'Builder', 'Types de contenu personnalisés'),
        ]:
            InstalledModule.objects.get_or_create(
                name=name,
                defaults={'label': label, 'description': desc, 'enabled': True},
            )

        Page.objects.get_or_create(
            slug='accueil',
            defaults={
                'title': 'Accueil',
                'content': 'Bienvenue dans ForgeCMS V0.',
                'is_published': True,
                'created_by': user,
            },
        )

        category, _ = Category.objects.get_or_create(name='Démo', slug='demo')
        Article.objects.get_or_create(
            slug='premier-article',
            defaults={
                'title': 'Premier article',
                'excerpt': 'Article de démonstration.',
                'content': 'ForgeCMS démarre avec un blog simple, puis évoluera vers une CMS Factory.',
                'category': category,
                'author': user,
                'is_published': True,
            },
        )

        ctype, _ = CustomContentType.objects.get_or_create(
            slug='vehicule',
            defaults={'name': 'Véhicule', 'description': 'Exemple de type de contenu métier'},
        )
        fields = [
            ('Marque', 'marque', 'text', True),
            ('Modèle', 'modele', 'text', True),
            ('Immatriculation', 'immatriculation', 'text', False),
            ('Date entretien', 'date_entretien', 'date', False),
        ]
        for order, (name, slug, field_type, required) in enumerate(fields):
            CustomField.objects.get_or_create(
                content_type=ctype,
                slug=slug,
                defaults={'name': name, 'field_type': field_type, 'required': required, 'order': order},
            )
        CustomEntry.objects.get_or_create(
            content_type=ctype,
            data={'marque': 'Peugeot', 'modele': '308', 'immatriculation': 'DEMO-001'},
            defaults={'is_published': True},
        )

        self.stdout.write(self.style.SUCCESS('Données de démonstration ajoutées.'))
