from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Task, Profile
import json
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate

def register(request):
    if request.method=="POST":
        username = request.POST.get('uname')
        password = request.POST.get('pwd')
        image = request.FILES.get('image')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return redirect('register')
        
        # Create the new user
        user = User.objects.create_user(
            username=username,
            password=password
        )
        
        # Create the user profile with the uploaded image (if any)
        Profile.objects.create(user=user, image=image)
        
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
        priority = request.POST.get('priority', 'Low')
        if title:
            Task.objects.create(user=request.user, title=title, priority=priority)
            
    # Sort tasks: Pending tasks first (False -> 0), then Completed (True -> 1), then mostly recent
    tasks = Task.objects.filter(user=request.user, is_deleted=False).order_by('completed', '-created_at')
    
    # Aggregating task completions by day to render the Github-style Heatmap Calendar
    # NOTE: This intentionally does NOT filter out 'is_deleted', natively preserving historical Heatmap data forever!
    completed_counts = (
        Task.objects.filter(user=request.user, completed=True, completed_at__isnull=False)
        .annotate(date=TruncDate('completed_at'))
        .values('date')
        .annotate(count=Count('id'))
    )
    
    # Build dictionary {"YYYY-MM-DD": count} safely
    heatmap_data = {
        obj['date'].strftime('%Y-%m-%d'): obj['count'] 
        for obj in completed_counts if obj['date']
    }
    
    heatmap_json = json.dumps(heatmap_data)
    
    # Account stats
    total_completed = Task.objects.filter(user=request.user, completed=True).count() # Lifetime
    total_pending = Task.objects.filter(user=request.user, completed=False, is_deleted=False).count()

    return render(request, 'dashboard.html', {
        'tasks': tasks,
        'heatmap_json': heatmap_json,
        'total_completed': total_completed,
        'total_pending': total_pending
    })


@login_required(login_url='login')
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.is_deleted = True
    task.save()
    return redirect('dashboard')

@login_required(login_url='login')
def complete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if not task.completed:
        task.completed = True
        task.completed_at = timezone.now()
    else:
        task.completed = False
        task.completed_at = None
    task.save()
    return redirect('dashboard')

@login_required(login_url='login')
def update_profile(request):
    if request.method == "POST":
        image = request.FILES.get('image')
        if image:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.image = image
            profile.save()
            messages.success(request, "Profile photo updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please choose an image to upload.")
            
    return render(request, 'update_profile.html')