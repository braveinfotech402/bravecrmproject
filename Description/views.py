from django.http import JsonResponse, HttpResponseNotAllowed
from client_app.models import Lead

import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404,render

from .models import  ActivityEntry
from django.utils.timezone import localtime

from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.views.decorators.http import require_POST

@csrf_exempt
@login_required
def add_activity(request, lead_id):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            note = body.get('note', '').strip()
            if not note:
                return JsonResponse({'error': 'Note is required'}, status=400)
            lead = Lead.objects.get(id=lead_id)
            activity = ActivityEntry.objects.create(
            lead=lead,
            note=note,
            created_by=request.user
            )
            return JsonResponse({
            'id': activity.id,
            'note': activity.note,
            'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'created_by_name': request.user.get_full_name(),
            'is_editable': True
            })
        except Lead.DoesNotExist:
            return JsonResponse({'error': 'Lead not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'Invalid method'}, status=405)




@login_required
def get_activities(request, lead_id):
    activities = ActivityEntry.objects.filter(lead_id=lead_id).select_related('created_by').order_by('-timestamp')
    activity_list = [{
        'id': activity.id,
        'note': activity.note,
        'timestamp': localtime(activity.timestamp).isoformat(),  # timezone-aware ISO8601 string
        'created_by_name': activity.created_by.get_full_name() if activity.created_by else 'Unknown',
        'is_editable': request.user == activity.created_by
    } for activity in activities]
    return JsonResponse({'activities': activity_list})


@csrf_exempt
@require_POST
@login_required
def edit_activity(request, activity_id):
    try:
        activity = ActivityEntry.objects.get(id=activity_id)
    except ActivityEntry.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    if activity.created_by != request.user:
        return HttpResponseForbidden("You do not have permission to edit this activity.")
    try:
        data = json.loads(request.body)
        note = data.get('note', '').strip()
        if not note:
            return HttpResponseBadRequest("Note cannot be empty.")
        activity.note = note
        activity.save()
        return JsonResponse({
            'id': activity.id,
            'note': activity.note,
            'timestamp': localtime(activity.timestamp).isoformat(),
            'created_by_name': request.user.get_full_name(),
            })
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON.")
    
    
    
@csrf_exempt
@require_POST
@login_required
def delete_activity(request, activity_id):
    try:
        activity = ActivityEntry.objects.get(id=activity_id)
    except ActivityEntry.DoesNotExist:
        return JsonResponse({'error': 'Activity not found'}, status=404)
    if activity.created_by != request.user:
        return HttpResponseForbidden("You do not have permission to delete this activity.")
    activity.delete()
    return JsonResponse({'status': 'deleted', 'id': activity_id})