from django.shortcuts import get_object_or_404, render
from .models import Article


def article_list(request):
    articles = Article.objects.filter(is_published=True)
    return render(request, 'blog/list.html', {'articles': articles})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'blog/detail.html', {'article': article})
