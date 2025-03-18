from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def staff_required(view_func):
    """Decorator to check if the user is authenticated and is a staff member."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(
                request, "You do not have permission to perform this action.", extra_tags='danger')
            return redirect(reverse('modular_engine:module_list'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view
