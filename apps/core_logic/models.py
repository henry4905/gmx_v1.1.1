from django.db import models

class NotificationTemplate(models.Model):
    code = models.CharField(max_length=100, unique=True)
    text = models.TextField()

    def __str__(self):
        return self.code





"""  ------------------------------------------
-------   Տեքստային ռեդակտորի բաժին      ------
-------                                  ------
----------------------------------------------- """
class Section(models.Model):
    name = models.CharField(max_length=100)

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subsections'
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

class Content(models.Model):
    code = models.PositiveIntegerField(unique=True)  # Արագ գտնելու համար (1, 2, 3...)

    title = models.CharField(max_length=300)

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="contents"
    )

    content = models.TextField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)   # Երբ ավելացվել է
    updated_at = models.DateTimeField(auto_now=True)       # Երբ փոփոխվել է

    def __str__(self):
        return f"{self.code} - {self.title}"


class ContentImage(models.Model):
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="content_images/")

    def __str__(self):
        return f"Image for {self.content.title}"