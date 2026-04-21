from django.db import models
from django.contrib.auth.models import User

from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageOps
import os
import subprocess
import tempfile

import uuid


from django.utils.text import slugify


from django_ckeditor_5.fields import CKEditor5Field

from io import BytesIO

try:
    import pikepdf
except ImportError:
    pikepdf = None




# Բուժաշխատող
class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    father_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    birth_year = models.IntegerField()
    birth_month = models.IntegerField()
    birth_day = models.IntegerField()

    # Նոր դաշտեր
    is_verified = models.BooleanField(default=False , verbose_name="էլ-հասցեն հաստատված է ")
    is_approved = models.BooleanField(default=False, verbose_name="Գործունեությունը թույլադրված է ")



    # ==================================================
    # ՆՈՐ ԴԱՇՏԵՐ (բոլորը optional)
    # ==================================================

    # Անձնական տվյալներ
    id_card_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="ID քարտի համար"
    )

    address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Հասցե"
    )

    # Մասնագիտական տվյալներ
    specialization = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Մասնագիտություն"
    )

    license_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Լիցենզիայի համար"
    )

    workplaces = models.TextField(
        null=True,
        blank=True,
        verbose_name="Աշխատանքի վայրեր"
    )

    # Ֆայլեր
    profile_photo = models.ImageField(
        upload_to='worker_photos/',
        null=True,
        blank=True,
        verbose_name="Նկար"
    )

    documents = models.FileField(
        upload_to='worker_documents/',
        null=True,
        blank=True,
        verbose_name="Փաստաթղթեր"
    )

    

    # --------------------------------------------------
    # Վերիֆիկացիայի համակարգ
    # --------------------------------------------------

    VERIFIED_BY_CHOICES = (
        ('admin', 'Ադմին'),
        ('registry', 'Պետական ռեգիստր'),
        ('external', 'Արտաքին աղբյուր'),
    )

    verified_by = models.CharField(
        max_length=20,
        choices=VERIFIED_BY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացրել է"
    )

    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Ընթացքի մեջ'),
        ('approved', 'Հաստատված է'),
        ('rejected', 'Մերժված է'),
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացիայի ստատուս"
    )

    # Ծառայողական
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

# Բուժհաստատություն
class FacilityProfile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    father_name = models.CharField(max_length=255, null=True)
    facility_name = models.CharField(max_length=255)
    factory_license_number = models.CharField(max_length=255,null=True)
    phone = models.CharField(max_length=20)
    fac_address = models.CharField(max_length=255,null=True)

    # Նոր դաշտեր
    is_verified = models.BooleanField(default=False, verbose_name="էլ-հասցեն հաստատված է ")
    is_approved = models.BooleanField(default=False, verbose_name="Գործունեությունը թույլադրված է ")


    # Անձնական տվյալներ
    id_card_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="ID քարտի համար"
    )

    # -------- Նոր դաշտերը (optional) ----------
    # Վերիֆիկացիայի համակարգ
    VERIFIED_BY_CHOICES = (
        ('admin', 'Ադմին'),
        ('registry', 'Պետական ռեգիստր'),
        ('external', 'Արտաքին աղբյուր'),
    )
    verified_by = models.CharField(
        max_length=20,
        choices=VERIFIED_BY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացրել է"
    )

    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Ընթացքի մեջ'),
        ('approved', 'Հաստատված է'),
        ('rejected', 'Մերժված է'),
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացիայի ստատուս"
    )

    # Ֆայլեր և նկարներ
    license_documents = models.FileField(
        upload_to='facility_documents/',
        null=True,
        blank=True,
        verbose_name="Լիցենզիայի փաստաթղթեր"
    )

    logo = models.ImageField(
        upload_to='facility_logos/',
        null=True,
        blank=True,
        verbose_name="Լոգո"
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    

    def __str__(self):
        return self.facility_name



# ===============================
# FACILITY WORK PHONES
# ===============================
class FacilityWorkPhone(models.Model):
    facility = models.ForeignKey(
        FacilityProfile,
        on_delete=models.CASCADE,
        related_name="work_phones"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Աշխատանքային հեռախոսահամար"
    )

    def __str__(self):
        return f"{self.facility.facility_name} - {self.phone}"














class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message















# =========================================
# Մատակարար / Արտադրող
# =========================================
class ImporterProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='importer_profile'
    )

    company_name = models.CharField(
        max_length=255,
        verbose_name="Ընկերության անվանում"
    )

    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Slug"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Ղեկավարի / հիմնական կոնտակտի հեռախոս"
    )

    email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Էլ. հասցե"
    )

    is_verified = models.BooleanField(
        default=False,
        verbose_name="Էլ-հասցեն հաստատված է"
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name="Գործունեությունը թույլադրված է"
    )


    google_map_embed = models.TextField(
    null=True,
    blank=True,
    verbose_name="Google քարտեզ (embed iframe)"
    )
    
    VERIFIED_BY_CHOICES = (
        ('admin', 'Ադմին'),
        ('registry', 'Պետական ռեգիստր'),
        ('external', 'Արտաքին աղբյուր'),
    )
    verified_by = models.CharField(
        max_length=20,
        choices=VERIFIED_BY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացրել է"
    )

    VERIFICATION_STATUS_CHOICES = (
        ('pending', 'Ընթացքի մեջ'),
        ('approved', 'Հաստատված է'),
        ('rejected', 'Մերժված է'),
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        null=True,
        blank=True,
        verbose_name="Վերիֆիկացիայի ստատուս"
    )

    is_certified = models.BooleanField(
        default=False,
        verbose_name="Սերտիֆիկացված է"
    )

    logo = models.FileField(
        upload_to='importer_logos/',
        null=True,
        blank=True,
        verbose_name="Լոգո"
    )

    short_info = models.TextField(
        null=True,
        blank=True,
        verbose_name="Կարճ ինֆո"
    )

    main_info = CKEditor5Field(
        'Հիմնական ինֆո',
        config_name='extends',
        null=True,
        blank=True
    )

    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Հիմնադրման տարեթիվ"
    )

    country = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Երկիր"
    )

    city = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Քաղաք"
    )

    address = models.TextField(
        null=True,
        blank=True,
        verbose_name="Հասցե"
    )

    websites = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Կայքեր / սոցցանցեր"
    )

    seo_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="SEO վերնագիր"
    )

    seo_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="SEO նկարագրություն"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Մատակարար"
        verbose_name_plural = "Մատակարարներ"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.logo:
            ext = os.path.splitext(self.logo.name)[1].lower()

            if ext != '.svg':
                try:
                    self.logo = self.compress_image(self.logo, self.logo.name)
                except Exception:
                    pass

        super().save(*args, **kwargs)

    def compress_image(self, uploaded_file, original_name):
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.webp"

        return ContentFile(output.getvalue(), name=new_name)

    def __str__(self):
        return self.company_name


# =========================================
# Հրապարակային աշխատանքային հեռախոսահամարներ
# =========================================
class ImporterWorkPhone(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name="work_phones",
        verbose_name="Մատակարար"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Աշխատանքային հեռախոսահամար"
    )

    class Meta:
        verbose_name = "Աշխատանքային հեռախոսահամար"
        verbose_name_plural = "Աշխատանքային հեռախոսահամարներ"

    def __str__(self):
        return f"{self.importer.company_name} - {self.phone}"


# =========================================
# Ընկերության սերտիֆիկատներ
# =========================================
class ImporterCertificate(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name="certificates",
        verbose_name="Մատակարար"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Սերտիֆիկատի անուն"
    )

    file = models.FileField(
        upload_to='importer_certificates/',
        null=True,
        blank=True,
        verbose_name="Ֆայլ / Նկար"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Սերտիֆիկատ"
        verbose_name_plural = "Սերտիֆիկատներ"
        ordering = ['-created_at', 'id']

    def save(self, *args, **kwargs):
        if self.file:
            file_name = self.file.name
            ext = os.path.splitext(file_name)[1].lower()

            if ext in ['.jpg', '.jpeg', '.png', '.webp']:
                self.file = self.compress_image(self.file, file_name)

            elif ext == '.pdf':
                compressed_pdf = self.compress_pdf(self.file, file_name)
                if compressed_pdf:
                    self.file = compressed_pdf

        super().save(*args, **kwargs)

    def compress_image(self, uploaded_file, original_name):
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.webp"

        return ContentFile(output.getvalue(), name=new_name)

    def compress_pdf(self, uploaded_file, original_name):
        if not pikepdf:
            return None

        input_pdf = BytesIO(uploaded_file.read())
        output_pdf = BytesIO()

        with pikepdf.open(input_pdf) as pdf:
            pdf.save(
                output_pdf,
                compress_streams=True,
                object_stream_mode=pikepdf.ObjectStreamMode.generate
            )

        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.pdf"

        return ContentFile(output_pdf.getvalue(), name=new_name)

    def __str__(self):
        return f"{self.importer.company_name} - {self.name}"


# =========================================
# Պայմանագրեր
# =========================================
class ImporterContract(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Մատակարար"
    )

    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Պայմանագրի անուն"
    )

    file = models.FileField(
        upload_to='importer_contracts/',
        null=True,
        blank=True,
        verbose_name="Պայմանագրի ֆայլ"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Պայմանագիր"
        verbose_name_plural = "Պայմանագրեր"
        ordering = ['-created_at', 'id']

    def __str__(self):
        return f"{self.importer.company_name} - {self.name or 'Պայմանագիր'}"


# =========================================
# Պարամետրերի տեսակներ
# =========================================
class ImporterParameterType(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Պարամետրի տեսակ"
    )

    class Meta:
        verbose_name = "Պարամետրի տեսակ"
        verbose_name_plural = "Պարամետրերի տեսակներ"
        ordering = ['name']

    def __str__(self):
        return self.name


# =========================================
# Պարամետր
# =========================================
class ImporterParameter(models.Model):
    VALUE_TYPE_CHOICES = (
        ('text', 'Տեքստ'),
        ('number', 'Թիվ'),
        ('choice', 'Ընտրովի'),
        ('file', 'Ֆայլ'),
        ('image', 'Նկար'),
        ('video', 'Վիդեո'),
        ('boolean', 'Առկա է / Առկա չէ'),
    )

    parameter_type = models.ForeignKey(
        ImporterParameterType,
        on_delete=models.CASCADE,
        related_name='parameters',
        verbose_name="Պարամետրի տեսակ"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Անվանում"
    )

    value_type = models.CharField(
        max_length=20,
        choices=VALUE_TYPE_CHOICES,
        default='text',
        verbose_name="Արժեքի տեսակ"
    )

    is_filterable = models.BooleanField(
        default=False,
        verbose_name="Ֆիլտրվող է"
    )

    class Meta:
        verbose_name = "Պարամետր"
        verbose_name_plural = "Պարամետրեր"
        ordering = ['parameter_type__name', 'name']

    def __str__(self):
        return self.name


# =========================================
# Ընտրովի արժեքներ
# =========================================
class ImporterParameterChoice(models.Model):
    parameter = models.ForeignKey(
        ImporterParameter,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Պարամետր"
    )

    value = models.CharField(
        max_length=255,
        verbose_name="Արժեք"
    )

    class Meta:
        verbose_name = "Ընտրովի արժեք"
        verbose_name_plural = "Ընտրովի արժեքներ"
        ordering = ['parameter__name', 'value']

    def __str__(self):
        return self.value


# =========================================
# Պարամետրի արժեք
# =========================================
class ImporterParameterValue(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name='parameter_values',
        verbose_name="Մատակարար"
    )

    parameter = models.ForeignKey(
        ImporterParameter,
        on_delete=models.CASCADE,
        related_name='importer_values',
        verbose_name="Պարամետր"
    )

    choice_value = models.ForeignKey(
        ImporterParameterChoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Ընտրված տարբերակ"
    )

    BOOLEAN_CHOICES = (
        (True, 'Առկա է'),
        (False, 'Առկա չէ'),
    )

    boolean_value = models.BooleanField(
        choices=BOOLEAN_CHOICES,
        null=True,
        blank=True,
        verbose_name="Առկա է / Առկա չէ"
    )

    text_value = models.TextField(
        null=True,
        blank=True,
        verbose_name="Տեքստային արժեք"
    )

    number_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Թվային արժեք"
    )

    file_value = models.FileField(
        upload_to='param_files/',
        null=True,
        blank=True,
        verbose_name="Ֆայլ"
    )

    image_value = models.ImageField(
        upload_to='param_images/',
        null=True,
        blank=True,
        verbose_name="Նկար"
    )

    video_value = models.FileField(
        upload_to='param_videos/',
        null=True,
        blank=True,
        verbose_name="Վիդեո"
    )

    class Meta:
        verbose_name = "Պարամետրի արժեք"
        verbose_name_plural = "Պարամետրերի արժեքներ"
        ordering = ['importer__company_name', 'parameter__name']
        unique_together = ('importer', 'parameter')

    def save(self, *args, **kwargs):
        if self.image_value:
            self.image_value = self.compress_image(self.image_value)

        if self.file_value:
            self.file_value = self.compress_pdf(self.file_value)

        if self.video_value:
            self.video_value = self.compress_video(self.video_value)

        super().save(*args, **kwargs)

    def compress_image(self, file):
        img = Image.open(file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        return ContentFile(output.getvalue(), name='compressed.webp')

    def compress_pdf(self, file):
        ext = os.path.splitext(file.name)[1].lower()

        if ext == '.pdf' and pikepdf:
            input_pdf = BytesIO(file.read())
            output_pdf = BytesIO()

            with pikepdf.open(input_pdf) as pdf:
                pdf.save(
                    output_pdf,
                    compress_streams=True,
                    object_stream_mode=pikepdf.ObjectStreamMode.generate
                )

            return ContentFile(output_pdf.getvalue(), name=file.name)

        return file

    def compress_video(self, file):
        input_temp = tempfile.NamedTemporaryFile(delete=False)
        output_temp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)

        for chunk in file.chunks():
            input_temp.write(chunk)

        input_temp.close()

        command = [
            'ffmpeg',
            '-i', input_temp.name,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            '-acodec', 'aac',
            output_temp.name
        ]

        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            return file

        with open(output_temp.name, 'rb') as f:
            data = f.read()

        return ContentFile(data, name='compressed_video.mp4')

    def __str__(self):
        return f"{self.importer.company_name} - {self.parameter.name}"


# =========================================
# Աշխատողներ
# =========================================
class ImporterEmployee(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name="Մատակարար"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Անուն"
    )

    position = models.CharField(
        max_length=255,
        verbose_name="Պաշտոն"
    )

    photo = models.ImageField(
        upload_to='importer_employees/',
        null=True,
        blank=True,
        verbose_name="Նկար"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Հերթականություն"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ակտիվ է"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Մատակարարի աշխատող"
        verbose_name_plural = "Մատակարարի աշխատողներ"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if self.photo:
            try:
                self.photo = self.compress_image(self.photo)
            except Exception:
                pass

        super().save(*args, **kwargs)

    def compress_image(self, file):
        img = Image.open(file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1200, 1200))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        return ContentFile(output.getvalue(), name='employee.webp')

    def __str__(self):
        return f"{self.importer.company_name} - {self.name}"




















class Brand(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    # ===== Հիմնական =====
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Բրենդ"
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Slug"
    )

    logo = models.ImageField(
        upload_to='brand_logos/',
        null=True,
        blank=True,
        verbose_name="Լոգո"
    )

    # ===== Կարճ / հիմնական ինֆո =====
    short_info = models.TextField(
        null=True,
        blank=True,
        verbose_name="Կարճ ինֆո"
    )

    main_info = CKEditor5Field(
        'Հիմնական ինֆո (երկար տեքստ)',
        config_name='extends',
        null=True,
        blank=True
    )

    # ===== Բիզնես ինֆո =====
    founded_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Հիմնադրման տարեթիվ"
    )

    country = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Երկիր"
    )

    websites = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Կայքերի հղումներ"
    )

    # ===== SEO =====
    seo_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="SEO վերնագիր"
    )

    seo_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="SEO նկարագրություն"
    )

    # ===== Կառավարում =====
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ակտիվ է"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Հերթականություն"
    )

    # ===== Ժամանակ =====
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="Ստեղծվել է"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name="Թարմացվել է"
    )

    class Meta:
        verbose_name = "Բրենդ"
        verbose_name_plural = "Բրենդներ"
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if self.logo and hasattr(self.logo, 'file'):
            try:
                self.logo = self.compress_image(self.logo, self.logo.name)
            except Exception:
                pass

        if not self.slug:
            base_slug = slugify(self.name) or str(self.id)[:8]
            slug = base_slug
            counter = 1

            while Brand.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def compress_image(self, uploaded_file, original_name):
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.webp"

        return ContentFile(output.getvalue(), name=new_name)

    def __str__(self):
        return self.name


class ImporterBrand(models.Model):
    importer = models.ForeignKey(
        ImporterProfile,
        on_delete=models.CASCADE,
        related_name='importer_brands'
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='brand_importers'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    

class BrandMedia(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('image', 'Նկար'),
        ('video', 'Վիդեո'),
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='media_items',
        verbose_name="Բրենդ"
    )

    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPE_CHOICES,
        verbose_name="Մեդիայի տեսակ"
    )

    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Անվանում"
    )

    file = models.FileField(
        upload_to='brand_media/',
        verbose_name="Ֆայլ"
    )

    preview_image = models.ImageField(
        upload_to='brand_media_previews/',
        null=True,
        blank=True,
        verbose_name="Preview նկար"
    )

    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Հերթականություն"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Ակտիվ է"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name="Ստեղծվել է"
    )

    class Meta:
        verbose_name = "Բրենդի մեդիա"
        verbose_name_plural = "Բրենդի մեդիաներ"
        ordering = ['order', 'id']

    def save(self, *args, **kwargs):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()

            if self.media_type == 'image' and ext in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    self.file = self.compress_image(self.file, self.file.name)
                except Exception:
                    pass

            elif self.media_type == 'video':
                try:
                    self.file = self.compress_video(self.file)
                except Exception:
                    pass

        if self.preview_image:
            try:
                self.preview_image = self.compress_image(self.preview_image, self.preview_image.name)
            except Exception:
                pass

        super().save(*args, **kwargs)

    def compress_image(self, uploaded_file, original_name):
        img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        img.thumbnail((1600, 1600))

        output = BytesIO()
        img.save(output, format='WEBP', quality=80, optimize=True)

        base_name = os.path.splitext(original_name)[0]
        new_name = f"{base_name}.webp"

        return ContentFile(output.getvalue(), name=new_name)

    def compress_video(self, file):
        input_temp = tempfile.NamedTemporaryFile(delete=False)
        output_temp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)

        for chunk in file.chunks():
            input_temp.write(chunk)

        input_temp.close()

        command = [
            'ffmpeg',
            '-i', input_temp.name,
            '-vcodec', 'libx264',
            '-crf', '28',
            '-preset', 'fast',
            '-acodec', 'aac',
            output_temp.name
        ]

        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open(output_temp.name, 'rb') as f:
                data = f.read()
            return ContentFile(data, name='compressed_video.mp4')
        except Exception:
            return file

    def __str__(self):
        return f"{self.brand.name} - {self.media_type}"