from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django import forms
from django.forms import Textarea
from django.utils.html import format_html

from .models import (
    WorkerProfile,

    FacilityProfile,
    FacilityWorkPhone,

    ImporterProfile,
    ImporterWorkPhone,
    ImporterCertificate,
    ImporterContract,
    ImporterEmployee,

    ImporterParameterType,
    ImporterParameter,
    ImporterParameterChoice,
    ImporterParameterValue,

    Brand,
    BrandMedia,
    ImporterBrand,
)


# ==================================================
# USER INLINE PROFILES
# ==================================================
class WorkerProfileInline(admin.StackedInline):
    model = WorkerProfile
    can_delete = False
    verbose_name_plural = "Բուժաշխատողի տվյալներ"


class FacilityProfileInline(admin.StackedInline):
    model = FacilityProfile
    can_delete = False
    verbose_name_plural = "Բուժհաստատության տվյալներ"


class ImporterProfileInline(admin.StackedInline):
    model = ImporterProfile
    can_delete = False
    verbose_name_plural = "Մատակարարի տվյալներ"


class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff')
    readonly_fields = ('id',)

    def get_inline_instances(self, request, obj=None):
        inlines = []
        if obj:
            try:
                if hasattr(obj, 'workerprofile'):
                    inlines.append(WorkerProfileInline(self.model, self.admin_site))
                elif hasattr(obj, 'facilityprofile'):
                    inlines.append(FacilityProfileInline(self.model, self.admin_site))
                elif hasattr(obj, 'importer_profile'):
                    inlines.append(ImporterProfileInline(self.model, self.admin_site))
            except Exception:
                pass
        return inlines


admin.site.unregister(User)
admin.site.register(User, UserAdmin)













# ==================================================
# IMPORTER FORMS / INLINES
# ==================================================
class ImporterProfileAdminForm(forms.ModelForm):
    class Meta:
        model = ImporterProfile
        fields = '__all__'
        widgets = {
            'short_info': Textarea(attrs={
                'rows': 4,
                'style': 'width:100%;'
            }),
            'websites': Textarea(attrs={
                'rows': 5,
                'style': 'width:100%; font-family:monospace;'
            }),
            'seo_description': Textarea(attrs={
                'rows': 4,
                'style': 'width:100%;'
            }),
            'address': Textarea(attrs={
                'rows': 3,
                'style': 'width:100%;'
            }),

            'google_map_embed': Textarea(attrs={
                'rows': 4,
                'style': 'width:100%; font-family:monospace;'
            }),
        }

    def clean_websites(self):
        websites = self.cleaned_data.get('websites')

        if not websites:
            return []

        if isinstance(websites, list):
            return [str(item).strip() for item in websites if str(item).strip()]

        raise forms.ValidationError(
            'Կայքերի հղումները պետք է լինեն list ձևաչափով, օրինակ՝ ["https://site1.com", "https://site2.com"]'
        )


class ImporterWorkPhoneInline(admin.TabularInline):
    model = ImporterWorkPhone
    extra = 1


class ImporterCertificateInline(admin.TabularInline):
    model = ImporterCertificate
    extra = 1


class ImporterContractInline(admin.TabularInline):
    model = ImporterContract
    extra = 1


class ImporterEmployeeInline(admin.TabularInline):
    model = ImporterEmployee
    extra = 1


# ==================================================
# IMPORTER WORK PHONE ADMIN
# ==================================================
@admin.register(ImporterWorkPhone)
class ImporterWorkPhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'importer', 'company_name', 'phone')
    search_fields = ('phone', 'importer__company_name', 'importer__user__username')
    list_filter = ('importer',)

    def company_name(self, obj):
        return obj.importer.company_name
    company_name.short_description = "Ընկերություն"


# ==================================================
# IMPORTER CERTIFICATE ADMIN
# ==================================================
@admin.register(ImporterCertificate)
class ImporterCertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'importer', 'certificate_name', 'file', 'created_at')
    search_fields = ('name', 'importer__company_name', 'importer__user__username')
    list_filter = ('importer', 'created_at')

    def certificate_name(self, obj):
        return obj.name
    certificate_name.short_description = "Սերտիֆիկատի անուն"


# ==================================================
# IMPORTER CONTRACT ADMIN
# ==================================================
@admin.register(ImporterContract)
class ImporterContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'importer', 'contract_name', 'file', 'created_at')
    search_fields = ('name', 'importer__company_name', 'importer__user__username')
    list_filter = ('importer', 'created_at')

    def contract_name(self, obj):
        return obj.name
    contract_name.short_description = "Պայմանագրի անուն"


# ==================================================
# IMPORTER EMPLOYEE ADMIN
# ==================================================
@admin.register(ImporterEmployee)
class ImporterEmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'importer', 'name', 'position', 'is_active', 'order', 'created_at')
    search_fields = ('name', 'position', 'importer__company_name')
    list_filter = ('is_active', 'importer', 'created_at')
    ordering = ('importer', 'order', 'id')


# ==================================================
# IMPORTER PARAMETER TYPE
# ==================================================
@admin.register(ImporterParameterType)
class ImporterParameterTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class ImporterParameterChoiceInline(admin.TabularInline):
    model = ImporterParameterChoice
    extra = 1


# ==================================================
# IMPORTER PARAMETER
# ==================================================
@admin.register(ImporterParameter)
class ImporterParameterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parameter_type', 'value_type', 'is_filterable')
    search_fields = ('name', 'parameter_type__name')
    list_filter = ('parameter_type', 'value_type', 'is_filterable')
    inlines = [ImporterParameterChoiceInline]


# ==================================================
# IMPORTER PARAMETER VALUE
# ==================================================
@admin.register(ImporterParameterValue)
class ImporterParameterValueAdmin(admin.ModelAdmin):
    list_display = ('id', 'importer', 'parameter', 'display_value')
    search_fields = (
        'importer__company_name',
        'parameter__name',
    )
    list_filter = ('parameter', 'parameter__value_type')

    def display_value(self, obj):
        if obj.choice_value:
            return obj.choice_value.value
        if obj.boolean_value is True:
            return "Առկա է"
        if obj.boolean_value is False:
            return "Առկա չէ"
        if obj.text_value:
            return obj.text_value
        if obj.number_value is not None:
            return obj.number_value
        if obj.file_value:
            return obj.file_value.name
        if obj.image_value:
            return obj.image_value.name
        if obj.video_value:
            return obj.video_value.name
        return "-"
    display_value.short_description = "Արժեք"


# ==================================================
# FACILITY WORK PHONE ADMIN
# ==================================================
@admin.register(FacilityWorkPhone)
class FacilityWorkPhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'facility', 'facility_name', 'phone')
    search_fields = ('phone', 'facility__facility_name', 'facility__user__username')
    list_filter = ('facility',)

    def facility_name(self, obj):
        return obj.facility.facility_name
    facility_name.short_description = "Բուժհաստատություն"












# ==================================================
# BRAND FORM
# ==================================================
class BrandAdminForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'short_info': Textarea(attrs={
                'rows': 4,
                'style': 'width:100%;'
            }),
            'websites': Textarea(attrs={
                'rows': 5,
                'style': 'width:100%; font-family:monospace;'
            }),
            'seo_description': Textarea(attrs={
                'rows': 4,
                'style': 'width:100%;'
            }),
        }

    def clean_websites(self):
        websites = self.cleaned_data.get('websites')

        if not websites:
            return []

        if isinstance(websites, list):
            return [str(item).strip() for item in websites if str(item).strip()]

        raise forms.ValidationError(
            'Կայքերի հղումները պետք է լինեն list ձևաչափով, օրինակ՝ ["https://site1.com", "https://site2.com"]'
        )


class BrandMediaInline(admin.TabularInline):
    model = BrandMedia
    extra = 1
    fields = (
        'media_type',
        'title',
        'file',
        'preview_image',
        'order',
        'is_active',
    )
    ordering = ('order', 'id')


class ImporterBrandInline(admin.TabularInline):
    model = ImporterBrand
    extra = 1
    autocomplete_fields = ('importer',)



@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    form = BrandAdminForm
    inlines = [BrandMediaInline, ImporterBrandInline]

    list_display = (
        'logo_preview',
        'name',
        'slug',
        'country',
        'founded_year',
        'is_active',
        'order',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'id',
        'name',
        'slug',
        'country',
        'short_info',
        'main_info',
        'seo_title',
        'seo_description',
    )

    list_filter = (
        'is_active',
        'country',
        'created_at',
        'updated_at',
    )

    readonly_fields = (
        'id',
        'logo_preview_large',
        'created_at',
        'updated_at',
    )

    ordering = ('order', 'name')
    list_per_page = 25
    save_on_top = True
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        ('Հիմնական տվյալներ', {
            'fields': (
                'id',
                'name',
                'slug',
                'logo',
                'logo_preview_large',
            )
        }),
        ('Ներկայացման տվյալներ', {
            'fields': (
                'short_info',
                'main_info',
            )
        }),
        ('Բիզնես տվյալներ', {
            'fields': (
                'founded_year',
                'country',
                'websites',
            ),
            'description': 'Օրինակ՝ ["https://site1.com", "https://site2.com"]'
        }),
        ('SEO տվյալներ', {
            'classes': ('collapse',),
            'fields': (
                'seo_title',
                'seo_description',
            )
        }),
        ('Կարգավորումներ', {
            'fields': (
                'is_active',
                'order',
            )
        }),
        ('Ժամանակային տվյալներ', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:contain;border-radius:8px;border:1px solid #ddd;background:#fff;padding:4px;" />',
                obj.logo.url
            )
        return "—"
    logo_preview.short_description = 'Լոգո'

    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="max-height:120px;max-width:220px;object-fit:contain;border-radius:10px;border:1px solid #ddd;background:#fff;padding:8px;" />',
                obj.logo.url
            )
        return "Լոգո չկա"
    logo_preview_large.short_description = 'Լոգոյի preview'


# ==================================================
# IMPORTER BRAND ADMIN
# ==================================================
@admin.register(ImporterBrand)
class ImporterBrandAdmin(admin.ModelAdmin):
    list_display = ('importer', 'brand', 'created_at')

    search_fields = (
        'importer__company_name',
        'brand__name',
    )

    list_filter = ('importer', 'brand')
    autocomplete_fields = ('importer', 'brand')


@admin.register(BrandMedia)
class BrandMediaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'brand',
        'media_type',
        'title',
        'order',
        'is_active',
        'created_at',
    )

    search_fields = (
        'brand__name',
        'title',
    )

    list_filter = (
        'brand',
        'media_type',
        'is_active',
    )

    readonly_fields = ('created_at',)
    ordering = ('brand', 'order', 'id')

    fieldsets = (
        ('Կապակցում', {
            'fields': ('brand',)
        }),
        ('Մեդիայի տվյալներ', {
            'fields': ('media_type', 'title', 'file', 'preview_image')
        }),
        ('Կարգավորումներ', {
            'fields': ('order', 'is_active')
        }),
        ('Ժամանակային տվյալներ', {
            'fields': ('created_at',)
        }),
    )