from .models import NotificationTemplate

def get_notification(code, **kwargs):
    try:
        template = NotificationTemplate.objects.get(code=code)
        return template.text.format(**kwargs)
    except NotificationTemplate.DoesNotExist:
        return ""
