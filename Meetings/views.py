from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Meeting

@login_required
def meeting_list(request):
    meetings = Meeting.objects.filter(client=request.user.client).order_by('-date')
    return render(request, 'meeting_list.html', {'meetings': meetings})

@login_required
def create_meeting(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        date = request.POST.get('date')
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        Meeting.objects.create(
            client=request.user.client,
            title=title,
            date=date,
            location=location,
            notes=notes
        )
        return redirect('meeting_list')
    return redirect('meeting_list')

