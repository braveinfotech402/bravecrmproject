from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import PhysicalProduct, DigitalProduct, Course, Service, PhysicalCategory,DigitalCategory,CourseCategory,ServiceCategory
import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

@csrf_exempt
def save_physical(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        try:
            category = PhysicalCategory.objects.get(id=category_id)
        except PhysicalCategory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=400)

        PhysicalProduct.objects.create(
            name=name,
            price=price,
            image=image,
            quantity=quantity,
            description=description,
            category=category
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)


@csrf_exempt
def save_digital(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        image = request.FILES.get('image')
       
        category_id = request.POST.get('category')

        try:
            category = DigitalCategory.objects.get(id=category_id)
        except DigitalCategory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=400)

        DigitalProduct.objects.create(
            name=name,
            price=price,
            image=image,
          
            category=category
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)


@csrf_exempt
def save_course(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        duration = request.POST.get('duration')
        fees = request.POST.get('fees')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        category_id = request.POST.get('category')

        try:
            category = CourseCategory.objects.get(id=category_id)
        except CourseCategory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=400)

        Course.objects.create(
            name=name,
            duration=duration,
            fees=fees,
            description=description,
            image=image,
            category=category
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)


@csrf_exempt
def save_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')

        try:
            category = ServiceCategory.objects.get(id=category_id)
        except ServiceCategory.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Category not found'}, status=400)

        Service.objects.create(
            name=name,
            category=category
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid'}, status=400)


def product_page(request):
    physicals = PhysicalProduct.objects.all()
    digitals = DigitalProduct.objects.all()
    courses = Course.objects.all()
    services = Service.objects.all()

    products = []

    for p in physicals:
        products.append({
            'id': p.id,
            'name': p.name,
            'type': 'physical',
            'price': p.price,
            'quantity': p.quantity,
            'image': p.image,
            'description': p.description,
            'category': p.category.id if p.category else '',
            'category_name': p.category.name if p.category else '',
        })

    for d in digitals:
        products.append({
            'id': d.id,
            'name': d.name,
            'type': 'digital',
            'price': d.price,
            'image': d.image,
            'category': d.category.id if d.category else '',
            'category_name': d.category.name if d.category else '',
        })

    for c in courses:
        products.append({
            'id': c.id,
            'name': c.name,
            'type': 'course',
            'price': c.fees,
            'quantity': '',  # Not applicable
            'image': c.image,
            'description': c.description,
            'category': c.category.id if c.category else '',
            'category_name': c.category.name if c.category else '',
        })

    for s in services:
        products.append({
            'id': s.id,
            'name': s.name,
            'type': 'service',
            'price': '',
            'quantity': '',
            'image': None,
            'category': s.category.id if s.category else '',
            'category_name': s.category.name if s.category else '',
        })
          # PAGINATION
    page_number = request.GET.get("page")
    paginator = Paginator(products, 10)  # 10 products per page
    page_obj = paginator.get_page(page_number)

    physical_categories = PhysicalCategory.objects.all()
    digital_categories = DigitalCategory.objects.all()
    course_categories = CourseCategory.objects.all()
    service_categories = ServiceCategory.objects.all()

    return render(request, 'product.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'physical_categories': physical_categories,
        'digital_categories': digital_categories,
        'course_categories': course_categories,
        'service_categories': service_categories,
    })




@csrf_exempt
def add_category_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        category_type = data.get('type', '').strip().lower()
        if not name:
            return JsonResponse({'success': False, 'error': 'Category name cannot be empty.'})
        if not category_type:
            return JsonResponse({'success': False, 'error': 'Category type is required.'})
        category_model_map = {
        'physical': PhysicalCategory,
        'digital': DigitalCategory,
        'course': CourseCategory,
        'service': ServiceCategory,
        }
        CategoryModel = category_model_map.get(category_type)
        if not CategoryModel:
            return JsonResponse({'success': False, 'error': f'Invalid category type: {category_type}'})
        if CategoryModel.objects.filter(name__iexact=name).exists():
            return JsonResponse({'success': False, 'error': f'{category_type.capitalize()} category already exists.'})
        category = CategoryModel.objects.create(name=name)
        return JsonResponse({
            'success': True,
            'category': {
            'id': category.id,
            'name': category.name
        }
            })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON in request body.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Unexpected error: {str(e)}'})




def _get_category_or_error(name, category_type):
    """Helper: return Category instance based on type and name, or None if not found."""
    model_map = {
        'physical': PhysicalCategory,
        'digital': DigitalCategory,
        'course': CourseCategory,
        'service': ServiceCategory,
    }
    CategoryModel = model_map.get(category_type.lower())
    if not CategoryModel:
        return None
    return CategoryModel.objects.filter(name=name).first()


@csrf_exempt
def update_physical(request):
    if request.method == 'POST':
        try:
            prod = get_object_or_404(PhysicalProduct, pk=request.POST.get('id'))
            prod.name = request.POST.get('name')
            prod.price = request.POST.get('price')
            prod.quantity = request.POST.get('quantity')
            prod.description = request.POST.get('description')

            cat_name = request.POST.get('category')
            cat = _get_category_or_error(cat_name, 'physical')  # ✅ Pass correct category_type
            if not cat:
                return JsonResponse({'success': False, 'message': 'Invalid category.'})

            prod.category = cat

            # Handle image update (optional)
            if 'image' in request.FILES:
                prod.image = request.FILES['image']

            prod.save()
            return JsonResponse({'success': True, 'message': 'Product updated! Please refresh the page..'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@csrf_exempt
def update_digital(request):
    if request.method == 'POST':
        prod = get_object_or_404(DigitalProduct, pk=request.POST.get('id'))
        prod.name = request.POST.get('name')
        prod.price = request.POST.get('price')
        

        cat_name = request.POST.get('category')
        cat = _get_category_or_error(cat_name,'digital')
        if not cat:
            return JsonResponse({'success': False, 'message': 'Invalid category.'})
        prod.category = cat

        prod.save()
        return JsonResponse({'success': True, 'message': 'Product updated! Please refresh the page..'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def update_course(request):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=request.POST.get('id'))
        course.name = request.POST.get('name')
        course.fees = request.POST.get('fees')
        course.description = request.POST.get('description')

        cat_name = request.POST.get('category')
        cat = _get_category_or_error(cat_name,'course')
        if not cat:
            return JsonResponse({'success': False, 'message': 'Invalid category.'})
        course.category = cat

        course.save()
        return JsonResponse({'success': True, 'message': 'Course updated! Please refresh the page..'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)


@csrf_exempt
def update_service(request):
    if request.method == 'POST':
        serv = get_object_or_404(Service, pk=request.POST.get('id'))
        serv.name = request.POST.get('name')

        cat_name = request.POST.get('category')
        cat = _get_category_or_error(cat_name,'service')
        if not cat:
            return JsonResponse({'success': False, 'message': 'Invalid category.'})
        serv.category = cat

        serv.save()
        return JsonResponse({'success': True, 'message': 'Service updated! Please refresh the page..'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

def delete_product(request, pk, product_type):
    if request.method == 'POST':
        # pick the right model
        if product_type == 'physical':
            obj = get_object_or_404(PhysicalProduct, pk=pk)
        elif product_type == 'digital':
            obj = get_object_or_404(DigitalProduct, pk=pk)
        elif product_type == 'course':
            obj = get_object_or_404(Course, pk=pk)
        elif product_type == 'service':
            obj = get_object_or_404(Service, pk=pk)
        else:
            messages.error(request, 'Unknown product type.')
            return redirect('product')

        name = getattr(obj, 'name', 'Item')
        obj.delete()
        messages.success(request, f'{product_type.title()} "{name}" deleted.')
        return redirect('product')

    # If someone GETs this URL, just bounce back
    return redirect('product')