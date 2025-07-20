from django.http import HttpResponseForbidden
from functools import wraps

def role_required(*roles):
    """
    Custom decorator to restrict access based on user roles.
    Usage: @role_required('is_client', 'is_reseller')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You are not authenticated.")
            if not any(getattr(request.user, role, False) for role in roles):
                return HttpResponseForbidden("You do not have access to this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
