# views.py
from django.shortcuts import render, redirect, get_object_or_404
from client_app.models import Lead, Column, Board, Tag
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

@login_required
def create_lead(request):
    if request.method == 'POST':
        board_id = request.POST.get('board_id')
        column_id = request.POST.get('column_id')
        column = get_object_or_404(Column, id=column_id)
        client = request.user.client if hasattr(request.user, 'client') else request.user.staff.client

        lead = Lead(
            client=client,
            column=column,
            title=request.POST.get('companyname'),
            firstname=request.POST.get('firstname'),
            lastname=request.POST.get('lastname'),
            streetaddress=request.POST.get('streetaddress'),
            streetnumber=request.POST.get('streetnumber'),
            postalcode=request.POST.get('postalcode'),
            city=request.POST.get('city'),
            country=request.POST.get('country'),
            state=request.POST.get('state'),
            phone=request.POST.get('phone'),
            companyname=request.POST.get('companyname'),
            tax=request.POST.get('tax'),
            email=request.POST.get('email')
        )

        if request.FILES.get('image'):
            lead.image = request.FILES['image']

        lead.save()

        # Handle tags
        tag_names = request.POST.get('tags', '').split(',')
        for name in tag_names:
            name = name.strip()
            if name:
                tag_obj, _ = Tag.objects.get_or_create(name=name)
                lead.tags.add(tag_obj)

        return redirect('board_details', board_id=column.board.id)

    # For GET requests, fetch board and column info
    board_id = request.GET.get('board_id')
    column_id = request.GET.get('column_id')
    board = get_object_or_404(Board, id=board_id)
    tags = Tag.objects.all()

    return render(request, 'createpipeline.html', {
        'board_id': board_id,
        'column_id': column_id,
        'tags': tags,
        'board':board,
    })
