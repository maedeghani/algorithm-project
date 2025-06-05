# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, LoginForm

# ثبت‌نام
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # ورود خودکار پس از ثبت‌نام
            return redirect('home')  # اینجا می‌تونی URL مقصد رو تغییر بدی
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# لاگین
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# لاگ‌اوت
def logout_view(request):
    logout(request)
    return redirect('login')
