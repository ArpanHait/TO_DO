from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Task

def register(request):
    if request.method=="POST":
        username = request.POST.get('uname')
        password = request.POST.get('pwd')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('register')
        
        # Create the new user
        user = User.objects.create_user(
            username=username,
            password=password
        )
        
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')
    
    return render(request,'register.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('uname')
        password = request.POST.get('pwd')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')
    

@login_required(login_url='login')
def dashboard(request):
    if request.method == "POST":
        title = request.POST.get('title')
        if title:
            Task.objects.create(user=request.user, title=title)
            
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'tasks': tasks})