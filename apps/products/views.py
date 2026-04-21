import json

from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.templatetags.static import static
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Product, ProductMedia, ProductAttributeValue, Category
from .filters import build_filtered_queryset, get_filter_options
from apps.accounts.models import ImporterWorkPhone

import requests
import xml.etree.ElementTree as ET


# =============================
# Helpers
# =============================

def serialize_products(queryset):
    products_data = []

    for product in queryset.distinct():
        image_url = static('images/no-image.jpg')

        if getattr(product, 'main_image', None):
            main_media = product.main_image[0]

            if getattr(main_media, 'thumbnail', None):
                image_url = main_media.thumbnail.url
            elif getattr(main_media, 'file', None):
                image_url = main_media.file.url

        products_data.append({
            'id': str(product.id),
            'name': product.name,
            'detail_url': f'/products/product/{product.id}/',
            'image_url': image_url,
        })

    return products_data





def get_cba_exchange_rates():
    url = "https://api.cba.am/exchangerates.asmx"

    soap_body = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                   xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
      <soap:Body>
        <ExchangeRatesLatest xmlns="http://www.cba.am/" />
      </soap:Body>
    </soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": "http://www.cba.am/ExchangeRatesLatest",
    }

    try:
        response = requests.post(url, data=soap_body.encode("utf-8"), headers=headers, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        rates = {
            "USD": None,
            "EUR": None,
            "RUB": None,
        }

        for elem in root.iter():
            tag = elem.tag.split("}")[-1]

            if tag == "ExchangeRate":
                iso_code = None
                rate_value = None
                amount_value = None

                for child in elem:
                    child_tag = child.tag.split("}")[-1]

                    if child_tag == "ISO":
                        iso_code = (child.text or "").strip()

                    elif child_tag == "Rate":
                        try:
                            rate_value = float((child.text or "").strip())
                        except (TypeError, ValueError):
                            rate_value = None

                    elif child_tag == "Amount":
                        try:
                            amount_value = float((child.text or "").strip())
                        except (TypeError, ValueError):
                            amount_value = None

                if iso_code in rates and rate_value:
                    if amount_value and amount_value != 0:
                        rates[iso_code] = rate_value / amount_value
                    else:
                        rates[iso_code] = rate_value

        return rates

    except Exception as e:
        print("CBA exchange rates error:", e)
        return {
            "USD": None,
            "EUR": None,
            "RUB": None,
        }

def get_category_descendants(category):
    descendants = []

    children = Category.objects.filter(
        parent=category,
        is_active=True
    ).order_by('name')

    for child in children:
        descendants.append(child)
        descendants.extend(get_category_descendants(child))

    return descendants


def get_products_base_queryset():
    return Product.objects.filter(
        is_active=True,
        importer__is_approved=True
    ).select_related(
        'brand',
        'country_of_manufacture',
        'importer',
        'category',
    ).prefetch_related(
        Prefetch(
            'media',
            queryset=ProductMedia.objects.filter(
                is_main=True,
                media_type='image'
            ),
            to_attr='main_image'
        )
    ).distinct()


# =============================
# Գլխավոր Products էջը
# =============================
@ensure_csrf_cookie
def productspage(request):
    products_list = get_products_base_queryset()

    paginator = Paginator(products_list, 16)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    current = products.number
    total = products.paginator.num_pages

    root_categories = Category.objects.filter(
        level=0,
        is_active=True
    ).order_by('name')

    if total <= 10:
        page_range = range(1, total + 1)
    else:
        start = max(current - 3, 1)
        end = min(current + 3, total)
        page_range = range(start, end + 1)

    context = {
        'products': products,
        'page_range': page_range,
        'total_pages': total,
        'root_categories': root_categories,
    }
    return render(request, 'products/products.html', context)


# =============================
# Product Detail էջ
# =============================

def product_detail(request, id):
    product = get_object_or_404(
        Product.objects.select_related('importer').prefetch_related(
            Prefetch(
                'attribute_values',
                queryset=ProductAttributeValue.objects.select_related(
                    'attribute',
                    'attribute__attribute_type'
                ).order_by(
                    'attribute__attribute_type__name',
                    'attribute__name'
                ),
                to_attr='ordered_attribute_values'
            ),
            Prefetch(
                'media',
                queryset=ProductMedia.objects.all().order_by('order', 'id')
            ),
            Prefetch(
                'importer__work_phones',
                queryset=ImporterWorkPhone.objects.all()
            ),
            'child_components__component_product',
            'component_groups__components__component_product',
        ),
        id=id
    )

    media = product.media.all()
    exchange_rates = get_cba_exchange_rates()


    context = {
        'product': product,
        'media': media,
        'exchange_rates': exchange_rates,
    }

    return render(request, 'products/product_detail.html', context)


# =============================
# Tree navigation API
# =============================

@require_POST
def filter_child_categories_api(request):
    try:
        data = json.loads(request.body or "{}")
        parent_id = data.get('parent_id')

        if not parent_id:
            return JsonResponse({
                'success': False,
                'message': 'parent_id is required',
                'categories': []
            }, status=400)

        categories = Category.objects.filter(
            parent_id=parent_id,
            is_active=True
        ).order_by('name')

        return JsonResponse({
            'success': True,
            'categories': [
                {
                    'id': str(category.id),
                    'name': category.name,
                }
                for category in categories
            ]
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e),
            'categories': []
        }, status=500)


# =============================
# Temporary simple category products API
# =============================

@require_POST
def filter_products_api(request):
    try:
        data = json.loads(request.body or "{}")
        category_id = data.get("category_id")
        include_descendants = bool(data.get("include_descendants", False))

        queryset = get_products_base_queryset()

        if category_id:
            category = Category.objects.get(id=category_id, is_active=True)

            if include_descendants:
                descendants = get_category_descendants(category)
                category_ids = [category.id] + [item.id for item in descendants]
                queryset = queryset.filter(category_id__in=category_ids)
            else:
                queryset = queryset.filter(category=category)

        products_data = serialize_products(queryset)

        return JsonResponse({
            'success': True,
            'count': len(products_data),
            'products': products_data,
        })

    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Category not found',
            'products': [],
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e),
            'products': [],
        }, status=500)


# =============================
# Main full filter API
# =============================

@require_POST
def filter_full_api(request):
    try:
        data = json.loads(request.body or "{}")
        if not isinstance(data, dict):
            data = {}

        base_qs = get_products_base_queryset()
        filtered_qs = build_filtered_queryset(base_qs, data)
        filter_options = get_filter_options(base_qs, data)
        products_data = serialize_products(filtered_qs)

        return JsonResponse({
            'success': True,
            'count': len(products_data),
            'products': products_data,
            'filter_options': filter_options,
            'selected_category': data.get('category'),
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e),
            'count': 0,
            'products': [],
            'filter_options': {
                'price': {
                    'min': None,
                    'max': None,
                    'selected_min': None,
                    'selected_max': None,
                },
                'brands': [],
                'countries': [],
                'importers': [],
                'statuses': [],
                'attributes': [],
                'custom_attributes': [],
                'importer_attributes': [],
            },
            'selected_category': data.get('category') if isinstance(data, dict) else None,
        }, status=500)