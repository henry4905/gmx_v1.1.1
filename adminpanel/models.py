from django.db import models

class SiteSettings(models.Model):
    logo = models.ImageField(upload_to='site_logos/', blank=True, null=True)
    logo_name = models.CharField(max_length=255, blank=True, null=True)
    logo_last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Settings"



class GMX(models.Model):
    system_name = models.CharField(max_length=255, default="GMX")

    superadm_n = models.CharField(max_length=255)
    superadm_m = models.CharField(max_length=255)
    superadm_f = models.CharField(max_length=255)

    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=50, blank=True, null=True)

    is_maintenance = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "GMX System"
        verbose_name_plural = "GMX System"

    def save(self, *args, **kwargs):
        # թույլ չտալ մեկից ավել record
        if not self.pk and GMX.objects.exists():
            raise ValueError("Միայն մեկ GMX record կարող է գոյություն ունենալ")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.system_name

