from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User

from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.views.decorators.csrf import csrf_exempt
import random
from django.contrib.auth.hashers import make_password



from django.utils.crypto import get_random_string
from django.utils.text import slugify

from .models import WorkerProfile, FacilityProfile, ImporterProfile
import uuid

sms_codes = {}
temp_users = {}

def login_page(request):
    if request.method == "POST":
        email = request.POST.get("username")  # form-ում username field, բայց email է
        password = request.POST.get("password")

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)

            # --- Debug info CMD-ում ---
            print("==== LOGIN DEBUG ====")
            print(f"User found: {user_obj}")
            print(f"Username: {user_obj.username}")
            print(f"Email: {user_obj.email}")
            print(f"is_active: {user_obj.is_active}")
            print(f"Password hash: {user_obj.password}")
            print(f"Authenticate returned: {user}")

        except User.DoesNotExist:
            print("==== LOGIN DEBUG ====")
            print(f"No user with email: {email}")
            user = None

        if user is not None:
            login(request, user)
            return redirect("welcome")
        else:
            messages.error(request, "Սխալ էլ.փոստ կամ գաղտնաբառ (տես CMD-ում debug)")

    return render(request, "accounts/login.html")


def register_view(request):
    return render(request, 'accounts/signup.html')

def registration_success_worker(request):
    return render(request, 'accounts/register_success.html')

def registration_success_pending(request):
    return render(request, 'accounts/register_success_pending.html')


@login_required
def welcome_page(request):
    user = request.user

    context = {
        "username": user.username,
        # Modal content (եթե պետք է բացվի սկզբից)
        "modal_html": get_modal_content(code="mail_verification", title="Ծանուցում"),
    }

    # Ներբեռնենք profile object-ը ու user type
    if hasattr(user, "workerprofile"):
        context["user_type"] = "worker"
        context["profile"] = user.workerprofile
    elif hasattr(user, "facilityprofile"):
        context["user_type"] = "facility"
        context["profile"] = user.facilityprofile
    elif hasattr(user, "importerprofile"):
        context["user_type"] = "importer"
        context["profile"] = user.importerprofile
    else:
        context["user_type"] = "unknown"
        context["profile"] = None

    print(context["profile"])

    print(vars(context["profile"]) if context["profile"] else "No profile")


    # Default section-ի template՝ settings
    # Սա կարող է օգտագործվել հենց template-ի մեջ նախնական բեռնման համար
    context["default_section"] = "settings"


    return render(request, "accounts/personal/profile_base.html", context)



def logout_page(request):
    logout(request)
    return redirect("homepage")

def create_pass_signup(request):
    return render(request, 'accounts/create_pass_login.html')

def registration_success(request):
    return render(request, 'accounts/registration_success.html')






def custom_password_reset(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_staff:
                messages.error(request, "Սխալ էլ. հասցե")  # Staff չեն կարող օգտագործել
                return render(request, "accounts/password_reset.html")
        except User.DoesNotExist:
            messages.error(request, "Սխալ էլ. հասցե")  # Եթե չկա բազայում
            return render(request, "accounts/password_reset.html")

        # Եթե օգտվող կա և staff չէ, անցնել ստանդարտ PasswordResetView
        return auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.html",
            success_url=reverse_lazy("password_reset_done")
        )(request)
    
    # GET request
    return render(request, "accounts/password_reset.html")




# --- Email Check ---
@csrf_exempt
def check_email(request):
    try:
        data = json.loads(request.body)
        email = data.get("email", "").strip()

        exists = User.objects.filter(email=email).exists()

        return JsonResponse({"exists": exists})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# --- Send SMS Code ---
@csrf_exempt
def send_sms_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        phone = data.get("phone")
        if not phone:
            return JsonResponse({"success": False, "error": "Phone required"})

        code = str(random.randint(100000, 999999))
        sms_codes[phone] = code
        print(f"DEBUG SMS CODE for {phone}: {code}")  # Փորձարկման համար

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


# --- Verify SMS Code and store temp data ---


from django.db.models import Max

@csrf_exempt
def verify_sms_code(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    data = json.loads(request.body)
    phone = data.get("phone")
    code = data.get("code")
    user_data = data.get("user_data", {})

    print("📥 Received data:", data)
    

    # ✅ SMS կոդի ստուգում
    if sms_codes.get(phone) != code:
        return JsonResponse({"success": False, "error": "Invalid SMS code"})

    user_type = user_data.get("type")
    password = user_data.get("password")

    # ===== USERNAME — հերթական =====
    last_user = User.objects.aggregate(max_id=Max("id"))["max_id"] or 0
    username = f"user{last_user + 1}"

    # ===== User fields ըստ type =====
    first_name = ""
    last_name = ""
    email = ""

    if user_type == "worker":
        first_name = user_data["w_firstname"]
        
        last_name = user_data.get("w_lastname", "")
        email = user_data.get("w_email", "")

    elif user_type == "facility":
        first_name = user_data.get("f_firstname", "")
        last_name = user_data.get("f_lastname", "")
        email = user_data.get("f_email", "")

    elif user_type == "importer":
        first_name = user_data.get("i_firstname", "")
        last_name = user_data.get("i_lastname", "")
        email = user_data.get("i_email", "")

    # ===== Ստեղծում ենք հիմնական User =====
    user = User.objects.create(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email
    )
    user.set_password(password)
    user.save()

    # ===== Ստեղծում ենք համապատասխան Profile =====
    if user_type == "worker":
        WorkerProfile.objects.create(
            user=user,
            father_name=user_data.get("w_fathername", ""),
            phone=phone,
            birth_year=int(user_data.get("w_birth_year", 1900)),
            birth_month=int(user_data.get("w_birth_month", 1)),
            birth_day=int(user_data.get("w_birth_day", 1)),
        )

    elif user_type == "facility":
        FacilityProfile.objects.create(
            user=user,
            facility_name=user_data.get("f_name", ""),
            phone=phone
        )

    elif user_type == "importer":
        ImporterProfile.objects.create(
            user=user,
            company_name=user_data.get("i_company", ""),
            phone=phone
        )

    # ===== Մաքրում ենք ժամանակավոր տվյալները =====
    sms_codes.pop(phone, None)
    temp_users.pop(phone, None)

    print(f"✅ User created: {username}")

    return JsonResponse({
        "success": True,
        "username": username
    })




""" ---------------------------------------------------
----------------------------------------------------------------
-------PROFILE VIEWS ------------------------------------------
-----------------------------------------------
----------------------------------
-------------------------------------------"""

from django.shortcuts import render
from django.http import Http404
from .models import Notification
from .models import WorkerProfile, FacilityProfile, ImporterProfile

"""def load_section(request, section_name):
    # Սկզբում բոլոր բաժինների template mapping-ը
    sections = {
        'settings': 'accounts/personal/sections/profile_settings.html',

        'notifications': 'accounts/personal/sections/notifications.html',

        'orders': 'accounts/personal/sections/orders.html',

        'messages': 'accounts/personal/sections/messages.html',

        'payments': 'accounts/personal/sections/payments.html',

        'rules': 'accounts/personal/sections/rules.html',

        'contracts': 'accounts/personal/sections/contracts.html',
    }

    template = sections.get(section_name)
    if not template:
        raise Http404("Section not found")

    context = {}

    # ==========================
    # User type & profile logic
    # ==========================
    user = request.user

    if hasattr(user, "workerprofile"):
        context["user_type"] = "worker"
        context["profile"] = user.workerprofile


    elif hasattr(user, "facilityprofile"):
        context["user_type"] = "facility"
        context["profile"] = user.facilityprofile


    elif hasattr(user, "importerprofile"):
        context["user_type"] = "importer"
        context["profile"] = user.importerprofile


    else:
        context["user_type"] = "unknown"
        context["profile"] = None


    # ==========================
    # Section-specific context
    # ==========================

    
    return render(request, template, context)



"""


from django.shortcuts import render, redirect
from django.http import Http404
from .models import WorkerProfile, FacilityProfile, ImporterProfile

def load_section(request, section_name):
    # Սկզբում բոլոր բաժինների template mapping-ը
    sections = {
        'settings': 'accounts/personal/sections/profile_settings.html',
        # 'messages': 'accounts/personal/sections/messages.html',  # Ջնջված
        'notifications': 'accounts/personal/sections/notifications.html',
        'orders': 'accounts/personal/sections/orders.html',
        'payments': 'accounts/personal/sections/payments.html',
        'rules': 'accounts/personal/sections/rules.html',
        'contracts': 'accounts/personal/sections/contracts.html',
    }

    # --------------------------------------
    # Հատուկ ստուգում 'messages' համար
    # --------------------------------------
    if section_name == "messages":
        # Եթե messages section է, redirect անենք մեր chat view
        # Օրինակ, եթե ուզում ենք ուղղակի chat_home
        return redirect("chat_home_personal")  # կամ start_chat view, ըստ նախագծի

    template = sections.get(section_name)
    if not template:
        raise Http404("Section not found")

    context = {}

    # ==========================
    # User type & profile logic
    # ==========================
    user = request.user

    if hasattr(user, "workerprofile"):
        context["user_type"] = "worker"
        context["profile"] = user.workerprofile
    elif hasattr(user, "facilityprofile"):
        context["user_type"] = "facility"
        context["profile"] = user.facilityprofile
    elif hasattr(user, "importerprofile"):
        context["user_type"] = "importer"
        context["profile"] = user.importerprofile
    else:
        context["user_type"] = "unknown"
        context["profile"] = None

    # ==========================
    # Section-specific context
    # ==========================

    return render(request, template, context)



from apps.core_logic.modals import get_modal_content

def profile_page(request):
    # Ստացնենք DB-ից modal text
    modal_html = get_modal_content(code="mail_verification", title="Ծանուցում")
    
    return render(request, 'accounts/personal/profile.html', {
        'modal_html': modal_html
    })

def chat_home_personal(request):
    return render(request, 'chat/chat_room.html')