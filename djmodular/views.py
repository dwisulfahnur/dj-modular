from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

def index(request):
    if request.user.is_authenticated:
        return redirect('modular_engine:module_list')
    return redirect('login')

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    success_url = '/module/'

    def get_success_url(self):
        return self.success_url