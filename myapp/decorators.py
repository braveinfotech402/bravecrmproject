from django.http import HttpResponseForbidden
from django.shortcuts import redirect
def superadmin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_client:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def reseller_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_client:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def client_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_client:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def staff_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def leads_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin:
            return HttpResponseForbidden("You are not authorized to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
