from django.contrib.auth import views as auth_views


from django.urls import path
from . import views

from .views import load_section

urlpatterns = [
    path("login/", views.login_page, name="login"),

    path("welcome/", views.welcome_page, name="welcome"),

    path("logout/", views.logout_page, name="logout"),

    path("password-reset/", views.custom_password_reset, name="password_reset"),

    path('register/', views.register_view, name='register'),

    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),



    path('register/check_email/', views.check_email, name='check_email'),

    path('register/send_sms_code/', views.send_sms_code, name='send_sms_code'),

    path('register/verify_sms_code/', views.verify_sms_code, name='verify_sms_code'),

    path('register/password/', views.create_pass_signup, name='create_pass_signup'),

    path('register/check_worker_email/', views.check_email, name='check_email'),

    path('register/success/worker/', views.registration_success_worker, name='registration_success_worker'),

    path('register/success/pending/', views.registration_success_pending, name='registration_success_pending'),

    path('welcome/accounts/personal/section/<str:section_name>/', load_section, name='load_section'),

]   
