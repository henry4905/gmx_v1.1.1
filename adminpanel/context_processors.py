# context_processors.py
from .models import SiteSettings

def site_settings_processor(request):
    return {'site_settings': SiteSettings.objects.first()}
