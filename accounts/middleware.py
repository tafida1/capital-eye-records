from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    """
    If a staff account is marked must_change_password=True,
    force the user to change password before using the system.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            allowed_paths = [
                reverse("change_own_password"),
                reverse("logout"),
            ]

            if request.path.startswith("/admin/"):
                return self.get_response(request)

            if getattr(request.user, "must_change_password", False):
                if request.path not in allowed_paths:
                    return redirect("change_own_password")

        return self.get_response(request)