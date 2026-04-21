from django import template
from apps.products.models import Category

register = template.Library()  # սա պարտադիր է

@register.simple_tag
def get_active_categories():
    """
    Վերադարձնում է բոլոր ակտիվ Category-ները
    """
    return Category.objects.filter(is_active=True).order_by('name')