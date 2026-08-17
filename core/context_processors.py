from .models import SiteSetting


def site_settings(request):
    settings_obj = SiteSetting.objects.first()
    if not settings_obj:
        settings_obj = SiteSetting(site_name='ForgeCMS')
    return {'site_settings': settings_obj}
