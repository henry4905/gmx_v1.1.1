from django.contrib import admin

# admin.py


from .models import GMX

@admin.register(GMX)
class GMXAdmin(admin.ModelAdmin):
    list_display = ("system_name", "is_maintenance", "updated_at")