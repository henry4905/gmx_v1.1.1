"""
URL configuration for gmx project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.contrib.sitemaps.views import sitemap
from apps.seo.sitemaps import StaticViewSitemap, ProductSitemap


sitemaps = {
    "static": StaticViewSitemap,
    "products": ProductSitemap,
}

urlpatterns = [

    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    
    path('admin/', admin.site.urls),

    path('adminpanel/', include('adminpanel.urls')),

    path('', include('apps.home.urls')),        # Home page
    path('about/', include('apps.about.urls')),
    path('products/', include('apps.products.urls')),
    path('vendors/', include('apps.vendors.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('help/', include('apps.help.urls')),
    path('standard/', include('apps.standard.urls')),

    path('core/', include('apps.core_logic.urls')),

    path("chat/", include("apps.chat.urls")),


    path('ckeditor5/', include('django_ckeditor_5.urls')),

]

# Media files development-ում
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)