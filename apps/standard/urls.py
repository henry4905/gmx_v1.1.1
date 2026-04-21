from django.urls import path
from . import views

urlpatterns = [
    path('', views.standardpage, name='standardpage'),

    
] 