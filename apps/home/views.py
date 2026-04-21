from django.shortcuts import render, get_object_or_404

from apps.core_logic.models import Section, Content, ContentImage

from django.core.paginator import Paginator



from apps.accounts.models import Brand
from apps.products.models import Product, ProductMedia



def homepage(request):
    brands = Brand.objects.filter(is_active=True).order_by('order', 'name')[:12]

    latest_products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:4].prefetch_related('media')

    for product in latest_products:
        product.main_image = product.media.filter(is_main=True).first()

    blog_section = Section.objects.filter(name__iexact="blog").first()
    latest_news = None

    if blog_section:
        subsection_ids = blog_section.subsections.values_list('id', flat=True)

        latest_news = Content.objects.filter(
            is_active=True,
            section_id__in=subsection_ids
        ).order_by('-created_at').first()

        if latest_news:
            latest_news.main_image = latest_news.images.first()

    context = {
        'brands': brands,
        'latest_products': latest_products,
        'latest_news': latest_news,
    }

    return render(request, 'home.html', context)



""" —--------------------------

--    ԲԼՈԳ ԷՋԻ ՀԱՄԱՐՐՐՐՐՐ
--
------------------------------- """



def vlogpage(request):
    blog_section = Section.objects.filter(name__iexact="blog").first()
    blog_subsections = blog_section.subsections.all() if blog_section else []

    selected_section = request.GET.get('section', 'all')

    if blog_section:
        subsection_ids = blog_subsections.values_list('id', flat=True)
        contents = Content.objects.filter(is_active=True, section_id__in=subsection_ids).order_by('-created_at')
        if selected_section != 'all':
            contents = contents.filter(section_id=selected_section)
    else:
        contents = Content.objects.filter(is_active=True).order_by('-created_at')
        if selected_section != 'all':
            contents = contents.filter(section_id=selected_section)

    paginator = Paginator(contents, 16)  # 4 cards per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "blog_subsections": blog_subsections,
        "page_obj": page_obj,
        "selected_section": selected_section,
    }
    return render(request, "vlog/blog.html", context)




def blog_detail(request, id):
    content = get_object_or_404(Content, id=id, is_active=True)

    # վերջին 4 նորությունները
    recent_contents = Content.objects.filter(
        is_active=True
    ).exclude(
        id=id
    ).order_by('-created_at')[:3]

    return render(request, 'vlog/blog_detail.html', {
        'content': content,
        'recent_contents': recent_contents,
    })





#====================================================
#====================================================
#============Importer page===========================
#====================================================
#====================================================

from django.shortcuts import render, get_object_or_404
from apps.accounts.models import (
    ImporterProfile,
    Brand,
    ImporterProfile,
    ImporterWorkPhone, 
    ImporterCertificate, 
    ImporterEmployee, 
    ImporterBrand,
)






def importer_detail(request, slug):
    importer = get_object_or_404(ImporterProfile, slug=slug)

    work_phones = importer.work_phones.all()
    certificates = importer.certificates.all()
    employees = importer.employees.filter(is_active=True).order_by('order', 'id')

    context = {
        'importer': importer,
        'work_phones': work_phones,
        'certificates': certificates,
        'employees': employees,
    }

    return render(request, 'importer/importer_detail.html', context)



from django.db.models import Prefetch

def importerspage(request):
    importers = (
        ImporterProfile.objects
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'importer_brands',
                queryset=ImporterBrand.objects.select_related('brand').filter(brand__is_active=True)
            )
        )
        .filter(is_approved=True)
        .order_by('company_name')
    )

    brands = Brand.objects.filter(is_active=True).order_by('name')

    context = {
        'importers': importers,
        'brands': brands,
    }
    return render(request, 'importer/importer.html', context)




def brand_detail(request, id):
    brand = get_object_or_404(
        Brand.objects.prefetch_related(
            'media_items',
            'brand_importers__importer',
        ),
        id=id,
        is_active=True
    )

    media_items = brand.media_items.filter(is_active=True).order_by('order', 'id')
    importers = brand.brand_importers.select_related('importer').all().order_by('id')

    context = {
        'brand': brand,
        'media_items': media_items,
        'importers': importers,
    }

    return render(request, 'importer/brand_detail.html', context)