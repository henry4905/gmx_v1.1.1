from django.urls import path
from . import views

from django.contrib.auth import views as auth_views



urlpatterns = [

    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    path('', views.admin_dashboard, name='admin_dashboard'),

    path('logout/', auth_views.LogoutView.as_view(next_page='/adminpanel/login/'), name='admin_logout'),

    path('<str:page>/', views.dynamic_page, name='dynamic_page'),

    


    path('categories/', views.category_tree_view, name='category_tree'),

    path('categories/edit/<uuid:object_id>/', views.edit_or_create_category_view, name='admin_edit_category'),
    path('categories/create/', views.edit_or_create_category_view, name='admin_create_category'),
    
    
    # Ավելացնել
    path('admin/attribute-type/add/', views.add_attribute_type, name='add_attribute_type'),

    # Ջնջել՝ ընդունում ենք UUID
    path(
        'admin/attribute-type/delete/<uuid:id>/',
        views.delete_attribute_type,
        name='delete_attribute_type'
    ),


    path('categories/', views.category_tree_view, name='category_tree'),


    path('<str:page>/', views.dynamic_page, name='dynamic_page'),
    path('<str:page>/<uuid:brand_id>/', views.dynamic_page, name='dynamic_page_with_id'),
]

  