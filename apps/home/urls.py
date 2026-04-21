from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),

    path('blog/', views.vlogpage, name='vlogpage'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),

    path('importers/', views.importerspage, name='importerspage'),

    path('importers/<slug:slug>/', views.importer_detail, name='importer_detail'),

    
   path('brands/<uuid:id>/', views.brand_detail, name='brand_detail'),

] 