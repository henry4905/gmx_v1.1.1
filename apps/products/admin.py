from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.db.models import Prefetch

from .models import (
    Category,
    CategoryAttribute,
    Product,
    ProductAttributeValue,
    AttributeRange,
    ProductComponentGroup,
    ProductComponent,
    CategoryComponentGroup,
    CategoryComponent,
    ProductMedia,
    CategoryAttributeType,
    ProductAttribute,
    ProductCustomAttributeValue,
    Country,
    AttributeChoice,
    ProductAttributeChoice,
    ProductDocument,
    ProductCertificate,
)


from apps.accounts.models import ImporterProfile


@admin.register(ImporterProfile)
class ImporterProfileAdmin(admin.ModelAdmin):
    search_fields = ['company_name', 'user__username']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


# ===============================
# ATTRIBUTE TYPE
# ===============================
@admin.register(CategoryAttributeType)
class CategoryAttributeTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_filterable']
    list_filter = ['is_filterable']
    search_fields = ['name']


# ===============================
# FORMS
# ===============================
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        if parent and parent == self.instance:
            raise forms.ValidationError("Category cannot be parent of itself")
        return cleaned_data


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1


class ProductCertificateInline(admin.TabularInline):
    model = ProductCertificate
    extra = 1

class CategoryAttributeForm(forms.ModelForm):
    class Meta:
        model = CategoryAttribute
        fields = '__all__'


class ProductMediaForm(forms.ModelForm):
    class Meta:
        model = ProductMedia
        fields = '__all__'


class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        attr = cleaned_data.get('attribute')

        value_text = cleaned_data.get('value_text')
        value_number = cleaned_data.get('value_number')
        value_boolean = cleaned_data.get('value_boolean')

        if not attr:
            return cleaned_data

        if attr.data_type == 'number':
            if value_number is None:
                raise forms.ValidationError(f"Attribute {attr.name} requires a number")

        elif attr.data_type == 'boolean':
            if value_boolean is None:
                raise forms.ValidationError(f"Attribute {attr.name} requires yes/no")

        elif attr.data_type == 'string':
            if not value_text:
                raise forms.ValidationError(f"Attribute {attr.name} requires text")

        elif attr.data_type == 'select':
            if not value_text:
                raise forms.ValidationError(f"Attribute {attr.name} requires selected value")
            if not attr.choices.filter(value=value_text).exists():
                raise forms.ValidationError(f"Attribute {attr.name} has no such choice")

        return cleaned_data


class AttributeRangeForm(forms.ModelForm):
    class Meta:
        model = AttributeRange
        fields = '__all__'


class ProductComponentForm(forms.ModelForm):
    class Meta:
        model = ProductComponent
        fields = '__all__'


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = '__all__'


class ProductCustomAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductCustomAttributeValue
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        attr = cleaned_data.get('attribute')
        product = cleaned_data.get('product')

        value_text = cleaned_data.get('value_text')
        value_number = cleaned_data.get('value_number')
        value_boolean = cleaned_data.get('value_boolean')

        if attr and product and attr.product_id != product.id:
            raise forms.ValidationError("Այս պարամետրը կապված չէ ընտրված product-ի հետ")

        if not attr:
            return cleaned_data

        if attr.data_type == 'number':
            if value_number is None:
                raise forms.ValidationError(f"Attribute {attr.name} requires a number")

        elif attr.data_type == 'boolean':
            if value_boolean is None:
                raise forms.ValidationError(f"Attribute {attr.name} requires yes/no")

        elif attr.data_type == 'string':
            if not value_text:
                raise forms.ValidationError(f"Attribute {attr.name} requires text")

        elif attr.data_type == 'select':
            if not value_text:
                raise forms.ValidationError(f"Attribute {attr.name} requires selected value")
            if not attr.choices.filter(value=value_text).exists():
                raise forms.ValidationError(f"Attribute {attr.name} has no such choice")

        return cleaned_data


# ===============================
# INLINES
# ===============================
class AttributeChoiceInline(admin.TabularInline):
    model = AttributeChoice
    extra = 0
    fields = ['value']
    verbose_name = "Choice"
    verbose_name_plural = "Choices"


class ProductAttributeChoiceInline(admin.TabularInline):
    model = ProductAttributeChoice
    extra = 0
    fields = ['value']
    verbose_name = "Choice"
    verbose_name_plural = "Choices"


class CategoryAttributeInline(admin.TabularInline):
    model = CategoryAttribute
    form = CategoryAttributeForm
    extra = 0
    show_change_link = True
    fields = [
        'attribute_type',
        'name',
        'data_type',
        'is_required',
        'is_main_filter',
        'unit'
    ]
    autocomplete_fields = ['attribute_type']
    verbose_name = "Attribute"
    verbose_name_plural = "Attributes"


class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    form = ProductAttributeValueForm
    extra = 0
    autocomplete_fields = ['attribute']
    fields = ['attribute', 'value_text', 'value_number', 'value_boolean']
    verbose_name = "Attribute Value"
    verbose_name_plural = "Attribute Values"


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    form = ProductAttributeForm
    extra = 0
    show_change_link = True
    autocomplete_fields = ['attribute_type']
    fields = [
        'attribute_type',
        'name',
        'data_type',
        'is_required',
        'is_main_filter',
        'unit'
    ]
    verbose_name = "Custom Attribute"
    verbose_name_plural = "Custom Attributes"


class ProductCustomAttributeValueInline(admin.TabularInline):
    model = ProductCustomAttributeValue
    form = ProductCustomAttributeValueForm
    extra = 0
    autocomplete_fields = ['attribute']
    fields = ['attribute', 'value_text', 'value_number', 'value_boolean']
    verbose_name = "Custom Attribute Value"
    verbose_name_plural = "Custom Attribute Values"


class AttributeRangeInline(admin.TabularInline):
    model = AttributeRange
    form = AttributeRangeForm
    extra = 0
    autocomplete_fields = ['attribute', 'product']
    fields = ['attribute', 'product', 'min_value', 'max_value']
    verbose_name = "Range"
    verbose_name_plural = "Ranges"


class ProductMediaInline(admin.TabularInline):
    model = ProductMedia
    form = ProductMediaForm
    extra = 1
    fields = ['file', 'media_type', 'thumbnail', 'is_main', 'order', 'media_preview']
    readonly_fields = ['media_preview']

    def media_preview(self, obj):
        if obj.media_type == 'image' and obj.file:
            return format_html(
                '<img src="{}" width="80" style="border-radius:5px;" />',
                obj.thumbnail.url if obj.thumbnail else obj.file.url
            )
        elif obj.media_type == 'video' and obj.file:
            return format_html(
                '<video width="120" controls><source src="{}" type="video/mp4"></video>',
                obj.file.url
            )
        return "-"
    media_preview.short_description = "Preview"


class ProductComponentInline(admin.TabularInline):
    model = ProductComponent
    form = ProductComponentForm
    extra = 0
    autocomplete_fields = ['component_product', 'group']
    fields = [
        'component_product',
        'group',
        'min_quantity',
        'max_quantity',
        'default_quantity',
        'is_required'
    ]
    verbose_name = "Component"
    verbose_name_plural = "Components"
    fk_name = 'parent_product'


# ===============================
# HELPERS
# ===============================
def get_obj_display_value(obj):
    if hasattr(obj, 'attribute') and obj.attribute:
        if obj.attribute.data_type == 'number':
            return obj.value_number
        if obj.attribute.data_type == 'boolean':
            return obj.value_boolean
    return obj.value_text


# ===============================
# ADMIN MODELS
# ===============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryForm
    list_display = ['name', 'parent', 'level', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active', 'level']
    search_fields = ['name', 'slug']
    inlines = [CategoryAttributeInline]
    ordering = ['level', 'name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Products"

    def save_model(self, request, obj, form, change):
        if obj.parent:
            obj.level = obj.parent.level + 1
        else:
            obj.level = 0
        super().save_model(request, obj, form, change)


@admin.register(CategoryAttribute)
class CategoryAttributeAdmin(admin.ModelAdmin):
    form = CategoryAttributeForm
    list_display = [
        'name',
        'category',
        'attribute_type',
        'data_type',
        'is_required',
        'is_main_filter',
        'unit',
        'range_count',
        'has_default_value',
        'default_value',
    ]
    list_filter = [
        'attribute_type',
        'data_type',
        'is_required',
        'is_main_filter',
        'category',
        'has_default_value'
    ]
    search_fields = ['name', 'category__name']
    inlines = [AttributeChoiceInline, AttributeRangeInline]
    autocomplete_fields = ['category', 'attribute_type']

    fields = [
        'category',
        'attribute_type',
        'name',
        'data_type',
        'unit',
        'is_required',
        'is_main_filter',
        'has_default_value',
        'default_value',
        'value_help_url',
    ]

    def range_count(self, obj):
        return obj.ranges.count()
    range_count.short_description = "Ranges"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'artikul',
        'name',
        'brand',
        'status',
        'standardisation_code',
        'country_of_manufacture',
        'category',
        'price_min',
        'price_max',
        'model_number',
        'importer',
        'is_active',
        'created_at',
        'attribute_summary',
        'custom_attribute_summary'
    ]

    list_filter = ['category', 'status', 'is_active', 'brand', 'country_of_manufacture', 'importer']
    search_fields = [
        'name',
        'category__name',
        'brand__name',
        'model_number',
        'status',
        'artikul',
        'standardisation_code',
        'country_of_manufacture__name',
    ]
    autocomplete_fields = ['category', 'importer', 'brand', 'country_of_manufacture']

    inlines = [
        ProductDocumentInline,
        ProductCertificateInline,
        ProductMediaInline,
        ProductAttributeValueInline,
        ProductAttributeInline,
        ProductCustomAttributeValueInline,
        AttributeRangeInline,
        ProductComponentInline
    ]

    ordering = ['category', 'name']

    def attribute_summary(self, obj):
        return ", ".join([
            f"{v.attribute.name}: {get_obj_display_value(v)}"
            for v in obj.attribute_values.all()
        ])
    attribute_summary.short_description = "Attributes"

    def custom_attribute_summary(self, obj):
        return ", ".join([
            f"{v.attribute.name}: {get_obj_display_value(v)}"
            for v in obj.custom_attribute_values.all()
        ])
    custom_attribute_summary.short_description = "Custom Attributes"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related(
            Prefetch(
                'attribute_values',
                queryset=ProductAttributeValue.objects.select_related('attribute')
            ),
            Prefetch(
                'custom_attribute_values',
                queryset=ProductCustomAttributeValue.objects.select_related('attribute')
            )
        )


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    form = ProductAttributeValueForm
    list_display = ['product', 'attribute', 'display_value']
    list_filter = ['attribute', 'product']
    search_fields = ['product__name', 'attribute__name']
    autocomplete_fields = ['attribute', 'product']

    def display_value(self, obj):
        return get_obj_display_value(obj)
    display_value.short_description = "Value"


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    form = ProductAttributeForm
    list_display = [
        'name',
        'product',
        'attribute_type',
        'data_type',
        'is_required',
        'is_main_filter',
        'unit',
        'created_at'
    ]
    list_filter = ['attribute_type', 'data_type', 'is_required', 'is_main_filter', 'product']
    search_fields = ['name', 'product__name']
    autocomplete_fields = ['product', 'attribute_type']
    inlines = [ProductAttributeChoiceInline]


@admin.register(ProductCustomAttributeValue)
class ProductCustomAttributeValueAdmin(admin.ModelAdmin):
    form = ProductCustomAttributeValueForm
    list_display = ['product', 'attribute', 'display_value']
    list_filter = ['product', 'attribute']
    search_fields = ['product__name', 'attribute__name']
    autocomplete_fields = ['product', 'attribute']

    def display_value(self, obj):
        return get_obj_display_value(obj)
    display_value.short_description = "Value"


@admin.register(AttributeRange)
class AttributeRangeAdmin(admin.ModelAdmin):
    form = AttributeRangeForm
    list_display = ['attribute', 'product', 'min_value', 'max_value']
    list_filter = ['attribute', 'product']
    search_fields = ['attribute__name', 'product__name']
    autocomplete_fields = ['attribute', 'product']


@admin.register(ProductComponentGroup)
class ProductComponentGroupAdmin(admin.ModelAdmin):
    list_display = ['product', 'name', 'min_select', 'max_select', 'is_required']
    list_filter = ['product', 'is_required']
    search_fields = ['product__name', 'name']


@admin.register(ProductComponent)
class ProductComponentAdmin(admin.ModelAdmin):
    form = ProductComponentForm
    list_display = [
        'parent_product',
        'component_product',
        'group',
        'min_quantity',
        'max_quantity',
        'default_quantity',
        'is_required'
    ]
    list_filter = ['parent_product', 'group', 'is_required']
    search_fields = ['parent_product__name', 'component_product__name', 'group__name']
    autocomplete_fields = ['parent_product', 'component_product', 'group']


@admin.register(CategoryComponentGroup)
class CategoryComponentGroupAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'min_select', 'max_select', 'is_required']
    list_filter = ['category', 'is_required']
    search_fields = ['category__name', 'name']


@admin.register(CategoryComponent)
class CategoryComponentAdmin(admin.ModelAdmin):
    list_display = [
        'category_group',
        'component_product',
        'min_quantity',
        'max_quantity',
        'default_quantity',
        'is_required'
    ]
    list_filter = ['category_group', 'is_required']
    search_fields = ['category_group__name', 'component_product__name']
    autocomplete_fields = ['category_group', 'component_product']


# ===============================
# MEDIA (JS)
# ===============================
class Media:
    js = ('admin/js/jquery.init.js', 'admin/js/custom_dynamic_inlines.js',)

@admin.register(ProductDocument)
class ProductDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'created_at')
    search_fields = ('title', 'product__name')
    list_filter = ('created_at',)


@admin.register(ProductCertificate)
class ProductCertificateAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'created_at')
    search_fields = ('title', 'product__name')
    list_filter = ('created_at',)