from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.db.models import Q

# Create your views here.

User = get_user_model()

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
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_exists = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=email)).exists()
        if user_exists:
            context['message'] = 'User already exists, please try another combination.'
        else:
            User.objects.create_user(username, email=email, password=password)
            return redirect('/login/')

    return render(request, 'auth/register.html', context=context)