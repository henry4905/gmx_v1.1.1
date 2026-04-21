from django.shortcuts import render, redirect, get_object_or_404
from django.apps import apps

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .helpers import get_notification
from .modals import get_modal_content

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import json
import random
"""------------------------------------------------------------------------
--------------------------


					ԾԱՆՈՒՑՒՈՄՆԵՐ

-------------------------------------------------------------------------------
------------------------ """
@require_POST
def get_modal_view(request):
    """
    Ստանում է:
    - code (պարտադիր)
    - այլ դաշտեր (name, email և այլն)՝ ըստ անհրաժեշտության
    Վերադարձնում է պատրաստ modal HTML
    """

    code = request.POST.get("code")

    if not code:
        return JsonResponse({"modal_html": ""})

    # Բոլոր մնացած դաշտերը վերցնում ենք որպես kwargs
    data = request.POST.dict()
    data.pop("code", None)

    # Ստանում ենք տեքստը kwargs-երով
    text = get_notification(code, **data)

    # Ստեղծում ենք modal HTML
    modal_html = get_modal_content(text=text)

    return JsonResponse({
        "modal_html": modal_html
    })



""" ---------------------------------------------------------
-
            Գրանցված օգտատիրոջ դուրս գալ էլ հասցեի փոփոխման ժամանակ
-
--------------------------------------------------------------"""



@csrf_exempt
def password_reset_done_ajax(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)  # օգտատերը դուրս է գալիս
        return JsonResponse({'status': 'ok', 'message': 'User logged out'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)







from apps.accounts.models import WorkerProfile, FacilityProfile, ImporterProfile

# =====================================
# Ուղարկել հաստատման կոդ
# =====================================
@csrf_exempt
@login_required
def send_verification_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")  # "phone" կամ "email"
        value = data.get("value")  # նոր արժեքը

        if not field or not value:
            return JsonResponse({"success": False, "error": "Անհրաժեշտ տվյալներ բացակայում են"})

        # Ստեղծել 6-անիշանի OTP
        otp_code = f"{random.randint(0, 999999):06d}"

        # Պահել session-ում՝ keyed ըստ field-ի
        request.session[f"verification_{field}"] = {
            "value": value,
            "otp": otp_code
        }
        request.session.modified = True

        # TODO: ուղարկել կոդը SMS կամ email
        print(f"Ուղարկված հաստատման կոդ {field}: {value} => {otp_code}")

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Անհավաստի պահանջ"})


# =====================================
# Հաստատել մուտքագրված կոդը
# =====================================
@csrf_exempt
@login_required
def verify_prof_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        field = data.get("field")  # "phone" կամ "email"
        code = data.get("code")    # մուտքագրված կոդ

        verification = request.session.get(f"verification_{field}")
        if not verification:
            return JsonResponse({"success": False, "error": "Կոդ չի գտնվել կամ ժամանակն ավարտված է"})

        if code == verification.get("otp"):
            new_value = verification.get("value")
            user = request.user

            # Որտեղ է profile-ը
            profile = None
            try:
                profile = WorkerProfile.objects.get(user=user)
            except WorkerProfile.DoesNotExist:
                try:
                    profile = FacilityProfile.objects.get(user=user)
                except FacilityProfile.DoesNotExist:
                    try:
                        profile = ImporterProfile.objects.get(user=user)
                    except ImporterProfile.DoesNotExist:
                        return JsonResponse({"success": False, "error": "Profile չի գտնվել"})

            # Թարմացնել համապատասխան դաշտը
            if field == "phone":
                profile.phone = new_value
            elif field == "email":
                user.email = new_value
                user.save()
                profile.is_verified = True  # email-ը վերիֆիկացված է

            profile.save()

            # Մաքրել session
            del request.session[f"verification_{field}"]
            request.session.modified = True

            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "error": "Սխալ հաստատման կոդ"})

    return JsonResponse({"success": False, "error": "Անհավաստի պահանջ"})



""" ------------------------------------------------------------
-

--
-
-       Մոդելների պարամետերերի արագ և ունիվերսալ փոփոխություն 
-
-
--
------------------------------------------------------------------"""



from django.shortcuts import render, redirect
from django import forms
from django.apps import apps



def edit_or_create_object(request, app_name, model_name, object_id=None):
    """
    Universal view ցանկացած model-ի create/update-ի համար
    - app_name: app-ի անունը (օր. 'products' կամ 'users')
    - model_name: model-ի անունը (օր. 'Category', 'Product', 'HealthcareWorker')
    - object_id: եթե կա → update, եթե չկա → create
    """

    model = apps.get_model(app_name, model_name)
    # Ստուգում console/logging-ում
    print("MODEL:", model)
    print("Model name:", model._meta.model_name)
    print("App label:", model._meta.app_label)



    obj = None
    if object_id:
        try:
            obj = model.objects.get(id=object_id)
        except model.DoesNotExist:
            obj = None  # չգտնվելու դեպքում ստեղծվում է նոր object
    

    print(model)
    DynamicForm = get_dynamic_form(model)


    if request.method == "POST":

        form = DynamicForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            # մնում ենք նույն էջում
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = DynamicForm(instance=obj)

    return render(request, "core_logic/dynamic_form.html", {"form": form})



def get_dynamic_form(model_class):
    class DynamicForm(forms.ModelForm):
        class Meta:
            model = model_class
            fields = '__all__'
    return DynamicForm  # <-- class է վերադարձվում, ոչ instance