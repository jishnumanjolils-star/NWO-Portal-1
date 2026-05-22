from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.conf import settings


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_paths = {
            reverse_lazy('login'),
            reverse_lazy('change_password'),
            reverse_lazy('logout'),
        }
        self.static_url = getattr(settings, 'STATIC_URL', '/static/')
        self.media_url = getattr(settings, 'MEDIA_URL', '/media/')

    def __call__(self, request):
        if request.user.is_authenticated:
            path = request.path
            if path not in self.exempt_paths and not path.startswith(self.static_url) and not path.startswith(self.media_url):
                profile = getattr(request.user, 'profile', None)
                if profile and profile.force_password_change:
                    return redirect('change_password')
        return self.get_response(request)
