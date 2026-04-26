from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.products.models import Product


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return [
            "homepage",
            "importerspage",
            "vlogpage",
            "productspage",
            "standardpage",
            "aboutpage",

        ]

    def location(self, item):
        return reverse(item)


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(
            is_active=True,
            importer__is_approved=True
        )

    def location(self, obj):
        return reverse("product_detail", kwargs={"id": obj.id})