from django.urls import path
from .views import get_modal_view

from . import views

urlpatterns = [
    # Ծանուցումները կանչելու համար նախատեսված հասցե
    path('modal/', get_modal_view, name='get_modal'),

    # Եթե օգտատերը իր գաղտնաբառն է փոխում այս հասցեն դուրս է հանում գրանցված օգտատիրոջը
    path('password-reset/ajax-done/', views.password_reset_done_ajax, name='password_reset_done_ajax'),


    path('send_verification_code/', views.send_verification_code, name='send_prof_verification_code'),

    path("verify_prof_code/", views.verify_prof_code, name="verify_prof_code"),
    
]
