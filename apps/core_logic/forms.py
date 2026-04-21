from django import forms
from django.apps import apps

def get_dynamic_form(app_name, model_name, instance=None):
    """
    Ստեղծում է dynamic ModelForm ցանկացած model-ի համար ցանկացած app-ից
    """
    model = apps.get_model(app_name, model_name)
    
    class DynamicForm(forms.ModelForm):
        class Meta:
            model = model
            fields = '__all__'
    
    return DynamicForm(instance=instance)



"""  -------------------------------------------------------

---------- Տեքստային ռեդակտորի մաս--------------------------

------------------------------------------------------------"""

from .models import Content


from django import forms
from .models import Content, Section


class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ["code", "title", "section", "content", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        sections = Section.objects.all().order_by('parent__id', 'name')

        choices = []
        for section in sections:
            if section.parent:
                choices.append((section.id, f"— {section.name}"))
            else:
                choices.append((section.id, section.name))

        self.fields['section'].choices = choices