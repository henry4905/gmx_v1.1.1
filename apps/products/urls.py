from django.urls import path
from . import views

urlpatterns = [
    path('', views.productspage, name='productspage'),

    path('product/<uuid:id>/', views.product_detail, name='product_detail'),

    path(
        'api/filter/categories/children/',
        views.filter_child_categories_api,
        name='filter_child_categories_api'
    ),

    path(
        'api/filter/products/',
        views.filter_products_api,
        name='filter_products_api'
    ),

    path(
        'api/filter/full/',
        views.filter_full_api,
        name='filter_full_api'
    ),
]