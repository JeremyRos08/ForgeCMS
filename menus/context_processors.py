from .models import Menu


def main_menu(request):
    menu = Menu.objects.filter(slug='main', is_active=True).first()
    items = menu.items.all() if menu else []
    return {'main_menu_items': items}
