from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

# Create your views here.

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username') or None
        password = request.POST.get('password') or None
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context['message'] = 'Wrong credentials entered. Please try again'
    return render(request, 'auth/login.html', context=context)

def register_view(request):
    return render(request, 'auth/register.html', {})