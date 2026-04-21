from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from django.http import JsonResponse

from .models import SiteSettings


from django.views.decorators.csrf import csrf_exempt

from apps.products.models import Category

from django.db.models import Q, Count







def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, "adminpanel/login.html", {"error": "Invalid credentials or no admin access"})

    return render(request, "adminpanel/login.html")



def admin_logout(request):
    logout(request)
    return redirect('admin_login')


@staff_member_required(login_url='/adminpanel/login/')
def admin_dashboard(request):
    settings, created = SiteSettings.objects.get_or_create(pk=1)

    if request.method == "POST" and request.FILES.get('logo'):
        uploaded = request.FILES['logo']
        settings.logo = uploaded
        settings.logo_name = uploaded.name
        settings.save()
        messages.success(request, "Լոգոն հաջողությամբ պահպանվեց։")
        return redirect('admin_dashboard')

    return render(request, "adminpanel/base.html", {'site_settings': settings})


""" --------------------------------------------------------------------------
------------------------
-----------------------    Dinamic menu
--------------------------------------------------------------------------------------"""
# views.py



def dynamic_page(request, page, brand_id=None):
    context = {}

    # Page → list of functions
    PAGE_LOGIC = {

        "text_redactor"  :      [content_editor],
        "atribute_class" :      [attribute_type_list],


    }

    for func in PAGE_LOGIC.get(page, []):
        context.update(func(request))  # ամեն ֆունկցիա վերադարձնում է context dict

    return render(request, f"adminpanel/pages/{page}.html", context)
    


""" ------------------------------
------------ Դասակարգման ադմին պանելում պահպանելու համար 
                արված առաջին քայլերը -------------------------
------------------------------------------------------------"""


def category_tree_view(request):
    """
    Ցուցադրում է բոլոր categories
    """
    return render(request, 'category_tree.html')


# category/views.py

from apps.core_logic.views import edit_or_create_object  # <-- ուրիշ app-ից
from django.apps import apps

def edit_or_create_category_view(request, object_id=None):
    """
    Սա ուղարկում է request-ը ու բոլոր needed arguments universal function-ին,
    որը գտնվում է ուրիշ app-ում
    """
    app_name = 'products'  # Category app-ի անունը, որտեղ model-ը ապրում է
    model = 'Category'

    
    # Օգտագործում ենք universal view-ը, որը dynamic form է ստեղծում
    return edit_or_create_object(request, app_name, model, object_id)



# -----------------------------------------------
#-----------------------------------------------
# Նկարի ավելացում մեր կոնետնետներին գրված տքստերին, աշխատում է
# Տեքստային ռեդակտորի հետ 
#-----------------------------------
#----------------------------------------------------


# adminpanel/views.py

from apps.core_logic.models import Content, ContentImage
from apps.core_logic.forms import ContentForm


def content_editor(request, content_id=None):
    """
    Այս ֆունկցիան միայն context է վերադարձնում,
    render կամ redirect չի անում
    """
    # Եթե content_id կա, վերցնում ենք գոյություն ունեցող Content
    if content_id:
        content = Content.objects.get(id=content_id)
        form = ContentForm(request.POST or None, instance=content)
    else:
        # Եթե չկա, ստեղծում ենք նոր Content
        form = ContentForm(request.POST or None)

    # POST handling՝ context-ի հետ, բայց առանց render վերադարձնելու
    if request.method == "POST":
        print("POST request received!")
        print(request.POST)  # ցույց կտա բոլոր ուղարկված դաշտերը
        if form.is_valid():
            form.save()
            return {"form": form, "saved": True}

    return {"form": form, "saved": False}




# —--------------------
#-----------------------------
# Պարամետրերի տեսակների վյուներ 
#------------------------------
#--------------------------


from apps.products.models import CategoryAttributeType




from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import redirect
from apps.products.models import CategoryAttributeType

# Ավելացնել Attribute Type
@require_POST
def add_attribute_type(request):
    name = request.POST.get("name")
    if name and not CategoryAttributeType.objects.filter(name=name).exists():
        CategoryAttributeType.objects.create(name=name)
    # Redirect դեպի dynamic_page, առանց dict վերադարձնելու
    return redirect("/adminpanel/atribute_class/")  # <-- redirect է dynamic_page

# Ջնջել Attribute Type
@require_POST
def delete_attribute_type(request, id):
    CategoryAttributeType.objects.filter(id=id).delete()
    # Redirect դեպի dynamic_page, dict ուղարկելու փորձ չկա
    return redirect("/adminpanel/atribute_class/")  # <-- redirect է dynamic_page

def attribute_type_list(request):
    return {"attribute_types": CategoryAttributeType.objects.all()}







