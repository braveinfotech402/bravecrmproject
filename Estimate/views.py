from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json

from .models import Estimate, EstimateItem, Lead
from Invoice.models import Invoice, InvoiceItem


def generate_estimate_number():
    today = timezone.now().strftime('%Y%m%d')
    count_today = Estimate.objects.filter(date__date=timezone.now().date()).count() + 1
    return f"EST-{today}-{count_today:03d}"


@require_POST
@csrf_protect
@login_required
def create_estimate_ajax(request):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request. Expected AJAX POST.'}, status=400)

    try:
        data = json.loads(request.body)

        lead_id = data.get('lead_id')
        estimate_number = data.get('estimate_number')
        customer_ref = data.get('customer_ref')
        issue_date = data.get('date')
        valid_until = data.get('valid_until')
        notes = data.get('notes', '')
        items = data.get('items', [])

        if not all([lead_id, estimate_number, issue_date, valid_until, items]):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        lead = Lead.objects.get(id=lead_id)
        client = lead.client
        staff = getattr(request.user, 'staff', None)

        subtotal = sum(float(item['price']) * int(item['qty']) for item in items)
        total = subtotal  # Add tax logic if needed

        estimate = Estimate.objects.create(
            client=client,
            lead=lead,
            created_by=staff,
            estimate_number=estimate_number,
            customer_ref=customer_ref,
            issue_date=issue_date,
            expiry_date=valid_until,
            notes=notes,
            subtotal=subtotal,
            total=total
        )

        for item in items:
            EstimateItem.objects.create(
                estimate=estimate,
                product_name=item['name'],
                quantity=int(item['qty']),
                price=float(item['price']),
                amount=int(item['qty']) * float(item['price'])
            )

        return JsonResponse({'success': True, 'estimate_id': estimate.id})

    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_GET
@login_required
def get_estimates_by_lead(request, lead_id):
    estimates = Estimate.objects.filter(lead_id=lead_id).select_related('client', 'lead')
    data = [
        {
            "id": e.id,
            "estimate_number": e.estimate_number,
            "client": e.client.user.get_full_name() if e.client else '',
            "lead": f"{e.lead.firstname} {e.lead.lastname}" if e.lead else '',
            "issue_date": e.issue_date.strftime("%B %d, %Y") if e.issue_date else '',
            "expiry_date": e.expiry_date.strftime("%B %d, %Y") if e.expiry_date else '',
            "status": e.status.title() if e.status else '',
            "total": float(e.total) if e.total else 0,
        }
        for e in estimates
    ]
    return JsonResponse({"estimates": data})


@csrf_exempt  # You can replace this with csrf_protect if you're handling CSRF in frontend
@login_required
def estimate_detail_view(request, estimate_id):
    estimate = get_object_or_404(Estimate.objects.select_related('lead'), id=estimate_id)

    if request.method == 'GET':
        items = EstimateItem.objects.filter(estimate=estimate)
        lead = estimate.lead
        lead_data = {
            'company_name': getattr(lead, 'company_name', ''),
            'address': getattr(lead, 'address', ''),
            'city': getattr(lead, 'city', ''),
            'state': getattr(lead, 'state', ''),
            'zip_code': getattr(lead, 'zip_code', ''),
            'email': getattr(lead, 'email', ''),
            'phone': getattr(lead, 'phone', ''),
        }

        return JsonResponse({
            'id': estimate.id,
            'lead_id': lead.id,
            'estimate_number': estimate.estimate_number,
            'customer_ref': estimate.customer_ref,
            'issue_date': estimate.issue_date.strftime('%Y-%m-%d'),
            'expiry_date': estimate.expiry_date.strftime('%Y-%m-%d'),
            'notes': estimate.notes,
            'lead': lead_data,
            'items': [
                {
                    'name': item.product_name,
                    'qty': item.quantity,
                    'price': float(item.price),
                    'amount': float(item.amount)
                }
                for item in items
            ]
        })

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            estimate.issue_date = datetime.strptime(data.get('issue_date'), '%Y-%m-%d').date()
            estimate.expiry_date = datetime.strptime(data.get('expiry_date'), '%Y-%m-%d').date()
            estimate.estimate_number = data.get('estimate_number', estimate.estimate_number)
            estimate.customer_ref = data.get('customer_ref', estimate.customer_ref)
            estimate.notes = data.get('notes', estimate.notes)
            estimate.save()

            EstimateItem.objects.filter(estimate=estimate).delete()
            for item in data.get('items', []):
                qty = int(item.get('qty', 0))
                price = float(item.get('price', 0))
                EstimateItem.objects.create(
                    estimate=estimate,
                    product_name=item.get('name'),
                    quantity=qty,
                    price=price,
                    amount=qty * price
                )

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)

    elif request.method == 'DELETE':
        estimate.delete()
        return JsonResponse({'success': True})

    return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@require_POST
@csrf_exempt  # Consider replacing with csrf_protect in production
@login_required
def convert_estimate_to_invoice(request, estimate_id):
    try:
        estimate = Estimate.objects.get(id=estimate_id)
    except Estimate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Estimate not found.'}, status=404)

    original_est_num = estimate.estimate_number
    invoice_num = f"INV-{original_est_num[4:]}" if original_est_num.startswith("EST-") else f"INV-{original_est_num}"

    invoice = Invoice.objects.create(
        client=estimate.client,
        lead=estimate.lead,
        created_by=estimate.created_by,
        invoice_number=invoice_num,
        customer_ref=estimate.customer_ref,
        issue_date=estimate.issue_date,
        due_date=estimate.expiry_date,
        status='unpaid',
        notes=estimate.notes,
        subtotal=estimate.subtotal,
        tax=estimate.tax,
        total=estimate.total,
    )

    for est_item in estimate.items.all():
        InvoiceItem.objects.create(
            invoice=invoice,
            product_name=est_item.product_name,
            quantity=est_item.quantity,
            price=est_item.price,
            amount=est_item.amount,
        )

    estimate.delete()

    return JsonResponse({'success': True, 'invoice_id': invoice.id, 'invoice_number': invoice.invoice_number})


@login_required
def estimate_list(request):
    if hasattr(request.user, 'client'):
        estimates = Estimate.objects.filter(client=request.user.client)
    else:
        estimates = Estimate.objects.all()
    return render(request, 'estimates_list.html', {'estimates': estimates})


@login_required
def get_lead_details(request, lead_id):
    try:
        lead = Lead.objects.get(id=lead_id)
        data = {
            'success': True,
            'firstname': lead.firstname,
            'lastname': lead.lastname,
            'email': lead.email,
            'phone': lead.phone,
            'company_name': getattr(lead, 'companyname', '') or getattr(lead, 'company_name', ''),
            'address': getattr(lead, 'streetaddress', '') or getattr(lead, 'address', ''),
        }
        return JsonResponse(data)
    except Lead.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lead not found'}, status=404)
