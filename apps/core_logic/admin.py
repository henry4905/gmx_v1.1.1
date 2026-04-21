from django.contrib import admin


from .models import NotificationTemplate

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'text')  # ադմինում ցուցադրվող դաշտերը
    search_fields = ('code', 'text')        # արագ որոնում code/text-ով
    ordering = ('id',)                      # կարգավորում ըստ ID



""" -------------------------------------------------
--------
--------    Տեքստային ռեդակտոր  —--------------------
-----------------------------------------------------"""


from .models import Section, Content, ContentImage


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")

# -----------------------------------------
# Inline նկարների համար
# -----------------------------------------
class ContentImageInline(admin.TabularInline):
    model = ContentImage
    extra = 1  # սկսում է մեկ դատարկ տողից



@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "title",
        "section",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = ("section", "is_active")
    search_fields = ("title", "code")
    ordering = ("code",)

    inlines = [ContentImageInline]  # <-- սա է նոր ավելացումը