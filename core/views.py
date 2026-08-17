from django.shortcuts import render
from pages.models import Page
from blog.models import Article
from builder.models import CustomContentType


def home(request):
    context = {
        'pages_count': Page.objects.count(),
        'articles_count': Article.objects.count(),
        'custom_types_count': CustomContentType.objects.count(),
        'latest_articles': Article.objects.filter(is_published=True)[:5],
    }
    return render(request, 'home.html', context)
