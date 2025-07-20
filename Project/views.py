# client_app/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project

@login_required
def project_list(request):
    projects = Project.objects.filter(client=request.user.client)
    return render(request, 'client_app/project_list.html', {'projects': projects})

@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        status = request.POST.get('status')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        budget = request.POST.get('budget') or 0

        Project.objects.create(
            name=name,
            status=status,
            start_date=start_date,
            end_date=end_date or None,
            budget=budget,
            client=request.user.client
        )
        return redirect('project_list')
    return redirect('project_list')

