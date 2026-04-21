from django.db import models
import uuid

from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image

from django_ckeditor_5.fields import CKEditor5Field

from apps.accounts.models import ImporterProfile, Brand
from django.db.models import Max


 

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "Country (Երկիր)"
        verbose_name_plural = "Countries (Երկրներ)"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children', on_delete=models.CASCADE
    )
    level = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    description = models.TextField(
    blank=True,
    null=True,
    verbose_name="Կարճ նկարագրություն"
    )

    help_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Լրիվ բացատրության հղում"
    )

    class Meta:
        verbose_name = "Category (ճյուղ)"
        verbose_name_plural = "Categories (ճյուղեր)"

    def __str__(self):
        return self.name


class CategoryAttributeType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)


    is_filterable = models.BooleanField(
        default=False,
        verbose_name="Ֆիլտրացիայի համար"
    )

    description = models.TextField(
    blank=True,
    null=True,
    verbose_name="Կարճ նկարագրություն"
    )

    help_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Լրիվ բացատրության հղում"
    )

    class Meta:
        verbose_name = "Attribute Type (Պարամետրի տեսակ)"
        verbose_name_plural = "Attribute Types (Պարամետրերի տեսակներ)"

    def __str__(self):
        return self.name




class CategoryAttribute(models.Model):
    DATA_TYPE_CHOICES = [
        ('string', 'Text (տեքստ)'),
        ('number', 'Number (թիվ)'),
        ('boolean', 'Yes/No (այո/ոչ)'),
        ('select', 'Select (ընտրություն)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='attributes'
    )

    attribute_type = models.ForeignKey(
        CategoryAttributeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attributes'
    )

    name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    is_required = models.BooleanField(default=False)
    unit = models.CharField(max_length=50, blank=True, null=True)

    # Quick filter / Advanced filter
    is_main_filter = models.BooleanField(
        default=False,
        verbose_name="Հիմնական ֆիլտր"
    )


    #  բազային արժեք ունի՞
    has_default_value = models.BooleanField(
        default=False,
        verbose_name="Բազային արժեք ունի"
    )

    #  բազային արժեք (text/number/boolean պահելու համար)
    default_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Բազային արժեք"
    )

    #  արժեքների հղում (documentation / help page)
    value_help_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Արժեքների հղում"
    )

    description = models.TextField(
    blank=True,
    null=True,
    verbose_name="Կարճ նկարագրություն"
    )

    class Meta:
        verbose_name = "Category Attribute (Կատեգորիայի պարամետր)"
        verbose_name_plural = "Category Attributes (Կատեգորիայի պարամետրեր)"

    def __str__(self):
        return f"{self.category.name} - {self.name}"



class ProductAttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='attribute_values'
    )

    attribute = models.ForeignKey(
        CategoryAttribute,
        on_delete=models.CASCADE
    )

    
    value_text = models.CharField(max_length=255, blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)

    class Meta:
        verbose_name = "Product Attribute Value"
        verbose_name_plural = "Product Attribute Values"

    def clean(self):
        if self.attribute.data_type == "number":
            if self.value_number is None:
                raise ValueError(f"{self.attribute.name} պետք է լինի թիվ")

        elif self.attribute.data_type == "boolean":
            if self.value_boolean is None:
                raise ValueError(f"{self.attribute.name} պետք է լինի boolean")

        elif self.attribute.data_type == "string":
            if not self.value_text:
                raise ValueError(f"{self.attribute.name} պետք է լինի տեքստ")

        elif self.attribute.data_type == "select":
            if not self.value_text:
                raise ValueError(f"{self.attribute.name} պետք է ընտրված արժեք ունենա")

            if not self.attribute.choices.filter(value=self.value_text).exists():
                raise ValueError(f"{self.attribute.name} համար նման ընտրանք չկա")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)




    def __str__(self):
        if self.attribute.data_type == "number":
            val = self.value_number
        elif self.attribute.data_type == "boolean":
            val = self.value_boolean
        else:
            val = self.value_text

        return f"{self.product.name} - {self.attribute.name}: {val}"






#================================================================================================
#================================================================================================
#                           Ապրանքքքքքք
#================================================================================================
#================================================================================================
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    artikul_number = models.PositiveIntegerField(editable=False, null=True, blank=True)
    artikul = models.CharField(max_length=20, editable=False, verbose_name="Արտիկուլ", blank=True)

    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='products')

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products',  null=True,
    blank=True)
    model_number = models.CharField(max_length=255, blank=True, null=True)

    country_of_manufacture = models.ForeignKey(Country,on_delete=models.PROTECT,null=True,blank=True,
    related_name='products')
    importer = models.ForeignKey(ImporterProfile, on_delete=models.PROTECT, blank=True, null=True)

    price_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, default='AMD')

    standardisation_code = models.CharField(max_length=20, blank=True, null=True)


    description = CKEditor5Field(
        'Ապրանքի նկարագրություն',
        config_name='extends',
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
    ('available', 'Առկա է'),
    ('unavailable', 'Առկա չէ'),
    ('on_order', 'Պատվերով'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name="Պրոդուկտի ստատուս"
    )
        

    def save(self, *args, **kwargs):
        if not self.artikul_number:
            last = Product.objects.aggregate(Max('artikul_number'))['artikul_number__max']
            self.artikul_number = (last + 1) if last else 10000

        self.artikul = f"GMX-{self.artikul_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class ProductDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Վերնագիր")
    description = models.TextField(blank=True, null=True, verbose_name="Կարճ նկարագրություն")
    file = models.FileField(upload_to='products/documents/', verbose_name="Փաստաթուղթ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Document (Ապրանքի փաստաթուղթ)"
        verbose_name_plural = "Product Documents (Ապրանքի փաստաթղթեր)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.file.name


class ProductCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Վերնագիր")
    description = models.TextField(blank=True, null=True, verbose_name="Կարճ նկարագրություն")
    file = models.FileField(upload_to='products/certificates/', verbose_name="Սերտիֆիկատ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Certificate (Ապրանքի սերտիֆիկատ)"
        verbose_name_plural = "Product Certificates (Ապրանքի սերտիֆիկատներ)"
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.file.name
        

class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, blank=True)
    file = models.FileField(upload_to='products/media/')
    thumbnail = models.ImageField(upload_to='products/media/thumbnails/', null=True, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_main=True),
                name='unique_main_media_per_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.media_type}"

    def save(self, *args, **kwargs):
        if self.file:
            ext = self.file.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'webp']:
                self.media_type = 'image'
            elif ext in ['mp4', 'webm', 'mov']:
                self.media_type = 'video'

        if self.is_main:
            ProductMedia.objects.filter(
                product=self.product,
                is_main=True
            ).exclude(id=self.id).update(is_main=False)

        if self.media_type == 'image' and self.file:
            img = Image.open(self.file)
            img = img.convert('RGB')

            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=75)
            self.file.save(self.file.name, ContentFile(buffer.getvalue()), save=False)
            buffer.close()

            thumbnail_size = (300, 300)
            img.thumbnail(thumbnail_size)
            thumb_buffer = BytesIO()
            img.save(thumb_buffer, format='JPEG', quality=75)
            thumb_name = f"thumb_{self.file.name}"
            self.thumbnail.save(thumb_name, ContentFile(thumb_buffer.getvalue()), save=False)
            thumb_buffer.close()

        super().save(*args, **kwargs)










class AttributeRange(models.Model):
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name='ranges')
    product = models.ForeignKey('Product', null=True, blank=True, on_delete=models.CASCADE, related_name='ranges')
    min_value = models.FloatField()
    max_value = models.FloatField()

    class Meta:
        verbose_name = "Attribute Range (Attribute-ի միջակայք)"
        verbose_name_plural = "Attribute Ranges (Attribute-ների միջակայքներ)"

    def __str__(self):
        return f"{self.attribute.name}: {self.min_value} - {self.max_value}"


# ================= Category-level Components =================
class CategoryComponentGroup(models.Model):
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='component_groups'
    )
    name = models.CharField(max_length=255)
    min_select = models.PositiveIntegerField(default=0)
    max_select = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class CategoryComponent(models.Model):
    category_group = models.ForeignKey(
        CategoryComponentGroup,
        on_delete=models.CASCADE,
        related_name='components'
    )
    component_product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT
    )
    min_quantity = models.PositiveIntegerField(default=1)
    max_quantity = models.PositiveIntegerField(default=1)
    default_quantity = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.category_group.category.name} - {self.component_product.name}"


# ================= Product-specific Component Groups =================
class ProductComponentGroup(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='component_groups'
    )
    name = models.CharField(max_length=255)
    min_select = models.PositiveIntegerField(default=0)
    max_select = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductComponent(models.Model):
    parent_product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='child_components'
    )
    group = models.ForeignKey(
        ProductComponentGroup,
        on_delete=models.CASCADE,
        related_name='components',
        null=True,
        blank=True
    )
    component_product = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        related_name='used_in_products'
    )
    min_quantity = models.PositiveIntegerField(default=1)
    max_quantity = models.PositiveIntegerField(default=1)
    default_quantity = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)

    class Meta:
        unique_together = ('parent_product', 'component_product')

    def __str__(self):
        return f"{self.parent_product.name} -> {self.component_product.name}"


class ProductAttribute(models.Model):
    DATA_TYPE_CHOICES = [
        ('string', 'Text (տեքստ)'),
        ('number', 'Number (թիվ)'),
        ('boolean', 'Yes/No (այո/ոչ)'),
        ('select', 'Select (ընտրություն)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='custom_attributes'
    )

    attribute_type = models.ForeignKey(
        CategoryAttributeType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='product_attributes'
    )

    name = models.CharField(max_length=255)
    data_type = models.CharField(max_length=20, choices=DATA_TYPE_CHOICES)
    is_required = models.BooleanField(default=False)
    unit = models.CharField(max_length=50, blank=True, null=True)

    # Quick filter / Advanced filter
    is_main_filter = models.BooleanField(
        default=False,
        verbose_name="Հիմնական ֆիլտր"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Attribute (Ապրանքի անհատական պարամետր)"
        verbose_name_plural = "Product Attributes (Ապրանքների անհատական պարամետրեր)"
        unique_together = ('product', 'name')

    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductCustomAttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='custom_attribute_values'
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name='values'
    )

    
    value_text = models.CharField(max_length=255, blank=True, null=True)
    value_number = models.FloatField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)

    class Meta:
        verbose_name = "Product Custom Attribute Value"
        verbose_name_plural = "Product Custom Attribute Values"
        unique_together = ('product', 'attribute')

    def clean(self):
        if self.attribute.product_id != self.product_id:
            raise ValueError("Այս պարամետրը կապված չէ տվյալ product-ի հետ")

        if self.attribute.data_type == "number":
            if self.value_number is None:
                raise ValueError(f"{self.attribute.name} պետք է լինի թիվ")

        elif self.attribute.data_type == "boolean":
            if self.value_boolean is None:
                raise ValueError(f"{self.attribute.name} պետք է լինի boolean")

        elif self.attribute.data_type == "string":
            if not self.value_text:
                raise ValueError(f"{self.attribute.name} պետք է լինի տեքստ")

        elif self.attribute.data_type == "select":
            if not self.value_text:
                raise ValueError(f"{self.attribute.name} պետք է ընտրված արժեք ունենա")
            if not self.attribute.choices.filter(value=self.value_text).exists():
                raise ValueError(f"{self.attribute.name} համար նման ընտրանք չկա")
    

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.attribute.data_type == "number":
            val = self.value_number
        elif self.attribute.data_type == "boolean":
            val = self.value_boolean
        else:
            val = self.value_text

        return f"{self.product.name} - {self.attribute.name}: {val}"


class ProductAttributeChoice(models.Model):
    attribute = models.ForeignKey('ProductAttribute', on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"

class AttributeChoice(models.Model):
    attribute = models.ForeignKey('CategoryAttribute', on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"