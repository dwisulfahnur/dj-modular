from django.contrib.auth.views import LoginView
from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    success_url = '/module/'

    def get_success_url(self):
        return self.success_url