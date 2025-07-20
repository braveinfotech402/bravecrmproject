import json
import logging
from datetime import datetime
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.dateparse import parse_date
from django.db import IntegrityError
from .models import Invoice, InvoiceItem
from client_app.models import Lead
from Products.models import PhysicalProduct,DigitalProduct,Course,Service
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_http_methods
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


def generate_next_invoice_number(request):
    lead_id = request.GET.get('lead_id')
    if not lead_id:
        return JsonResponse({'error': 'Lead ID is required'}, status=400)

    try:
        lead_id = int(lead_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid Lead ID'}, status=400)

    latest_invoice = Invoice.objects.filter(lead_id=lead_id).order_by('-id').first()
    next_number = 1
    if latest_invoice and latest_invoice.invoice_number:
        try:
            current_number = int(latest_invoice.invoice_number.split('-')[-1])
            next_number = current_number + 1
        except Exception:
            pass

    return JsonResponse({'invoice_number': f"INV-{str(next_number).zfill(4)}"})

@csrf_exempt
@require_POST
def create_invoice(request):
    data = json.loads(request.body)

    lead_id = data.get("lead_id")
    invoice_number = data.get("invoice_number")
    customer_ref = data.get("customer_ref", "")
    issue_date = data.get("issue_date")
    due_date = data.get("due_date")
    status = data.get("status")
    notes = data.get("notes", "")
    items = data.get("items", [])

    try:
        lead = Lead.objects.get(id=lead_id)
        client = lead.client
    except Lead.DoesNotExist:
        return JsonResponse({"error": "Lead not found."}, status=404)

    subtotal = Decimal("0.00")
    for item in items:
        subtotal += Decimal(item["qty"]) * Decimal(item["price"])

    tax = Decimal("0.00")  # You can change this logic later
    total = subtotal + tax

    invoice = Invoice.objects.create(
        lead=lead,
        client=client,
        invoice_number=invoice_number,
        customer_ref=customer_ref,
        issue_date=issue_date,
        due_date=due_date,
        status=status,
        notes=notes,
        subtotal=subtotal,
        tax=tax,
        total=total,
    )

    for item in items:
        InvoiceItem.objects.create(
            invoice=invoice,
            product_name=item["name"],
            quantity=item["qty"],
            price=item["price"],
            amount=Decimal(item["qty"]) * Decimal(item["price"]),
        )

    return JsonResponse({"success": True, "invoice_id": invoice.id})



@require_GET
def get_invoices_by_lead(request, lead_id):
    invoices = Invoice.objects.filter(lead_id=lead_id)
    data = []
    for inv in invoices:
        data.append({
            "id": inv.id,
            "invoice_number": inv.invoice_number,
            "customer_ref":inv.customer_ref,
            "notes":inv.notes,
            "client": str(inv.client),
            "total": float(inv.total),
            "status": inv.status,
            "issue_date": inv.issue_date.strftime('%Y-%m-%d'),
            "due_date": inv.due_date.strftime('%Y-%m-%d'),
            "download_url": inv.get_download_url() if hasattr(inv, "get_download_url") else "#"
        })
    return JsonResponse({"invoices": data})



@require_GET
def get_products_by_type(request):
    product_type = request.GET.get('type')

    if not product_type:
        return JsonResponse({'error': 'Missing product type'}, status=400)

    if product_type == 'physical':
        products = PhysicalProduct.objects.all()
        product_list = [
            {
                'name': p.name,
                'price': float(p.price),
                'id': p.id,
                'image': p.image.url if p.image else '',
                'description': p.description,
                'quantity': p.quantity,
            } for p in products
        ]

    elif product_type == 'digital':
        products = DigitalProduct.objects.all()
        product_list = [
            {
                'name': p.name,
                'price': float(p.price),
                'id': p.id,
                'image': p.image.url if p.image else '',
            } for p in products
        ]

    elif product_type == 'course':
        products = Course.objects.all()
        product_list = [
            {
                'name': p.name,
                'price': float(p.fees),
                'id': p.id,
                'description': p.description,
                'duration': p.duration,
                'image': p.image.url if p.image else '',
            } for p in products
        ]

    elif product_type == 'service':
        products = Service.objects.all()
        product_list = [
            {
                'name': p.name,
                'price': 0.00,
                'id': p.id,
            } for p in products
        ]
    else:
        return JsonResponse({'error': 'Invalid product type'}, status=400)

    return JsonResponse({'products': product_list})



@csrf_exempt
def invoice_detail(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return JsonResponse({"error": "Invoice not found."}, status=404)

    if request.method == "GET":
        items = [
            {
                "id": item.id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": float(item.price),
                "amount": float(item.amount),
            }
            for item in invoice.items.all()
        ]

        data = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_ref": invoice.customer_ref,
            "issue_date": invoice.issue_date.isoformat(),
            "due_date": invoice.due_date.isoformat(),
            "status": invoice.status,
            "notes": invoice.notes,
            "items": items,
        }
        return JsonResponse(data)

    elif request.method == "PUT":
        import json
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Update invoice fields
        invoice.invoice_number = data.get("invoice_number", invoice.invoice_number)
        invoice.customer_ref = data.get("customer_ref", invoice.customer_ref)
        invoice.issue_date = data.get("issue_date", invoice.issue_date)
        invoice.due_date = data.get("due_date", invoice.due_date)
        invoice.status = data.get("status", invoice.status)
        invoice.notes = data.get("notes", invoice.notes)
        invoice.save()

        # Update invoice items
        # First delete existing items
        invoice.items.all().delete()

        # Add new items
        items_data = data.get("items", [])
        for item_data in items_data:
            invoice.items.create(
                product_name=item_data.get("product_name", ""),
                quantity=item_data.get("quantity", 0),
                price=item_data.get("price", 0),
                amount=item_data.get("amount", 0),
            )

        return JsonResponse({"success": True})

    elif request.method == "DELETE":
        invoice.delete()
        return JsonResponse({"success": True})

    else:
        return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])

    
    
@csrf_exempt
@require_http_methods(["PUT"])
def update_invoice(request, invoice_id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return JsonResponse({"error": "Invoice not found."}, status=404)

    data = json.loads(request.body)

    try:
        invoice.invoice_number = data.get("invoice_number", invoice.invoice_number)
        invoice.customer_ref = data.get("customer_ref", invoice.customer_ref)
        invoice.issue_date = data.get("issue_date", invoice.issue_date)
        invoice.due_date = data.get("due_date", invoice.due_date)
        invoice.status = data.get("status", invoice.status)
        invoice.notes = data.get("notes", invoice.notes)

        items = data.get("items", [])

        # Clear old items
        invoice.items.all().delete()

        # Recalculate totals
        subtotal = Decimal("0.00")
        for item in items:
            quantity = Decimal(item["quantity"])
            price = Decimal(item["price"])
            amount = quantity * price
            subtotal += amount

            InvoiceItem.objects.create(
                invoice=invoice,
                product_name=item["product_name"],
                quantity=quantity,
                price=price,
                amount=amount,
            )

        tax = Decimal("0.00")  # You can add tax calculation logic here if needed
        total = subtotal + tax

        invoice.subtotal = subtotal
        invoice.tax = tax
        invoice.total = total
        invoice.save()

        # Prepare response data including items
        response_data = {
            "success": True,
            "invoice": {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "customer_ref": invoice.customer_ref,
                "issue_date": invoice.issue_date.strftime('%Y-%m-%d'),
                "due_date": invoice.due_date.strftime('%Y-%m-%d'),
                "status": invoice.status,
                "notes": invoice.notes,
                "subtotal": float(invoice.subtotal),
                "tax": float(invoice.tax),
                "total": float(invoice.total),
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "price": float(item.price),
                        "amount": float(item.amount),
                    }
                    for item in invoice.items.all()
                ],
            },
        }

        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    
    
@login_required
def invoice_list(request):
    if hasattr(request.user, 'client'):
        invoices = Invoice.objects.filter(client=request.user.client)
    else:
        invoices = Invoice.objects.all()
    
    return render(request, 'invoice_list.html', {'invoices': invoices})



