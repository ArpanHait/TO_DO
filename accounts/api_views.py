import datetime
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from .models import Task, Profile

def get_user_data(user):
    image_url = ""
    try:
        if user.profile and user.profile.image:
            image_url = user.profile.image.url
    except Profile.DoesNotExist:
        pass
    return {
        "id": user.id,
        "username": user.username,
        "image_url": image_url
    }

@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    image = request.FILES.get("image")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAR_ERROR if hasattr(status, 'HTTP_400_BAR_ERROR') else status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.create_user(username=username, password=password)
        profile = Profile.objects.create(user=user)
        if image:
            profile.image = image
            profile.save()
        
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user": get_user_data(user)
        }, status=status.HTTP_201_CREATED)
    except IntegrityError:
        return Response({"error": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "token": token.key,
        "user": get_user_data(user)
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({"success": "Logged out successfully."})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    image = request.FILES.get("image")
    if not image:
        return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)

    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.image = image
    profile.save()

    return Response({
        "success": "Profile photo updated successfully.",
        "user": get_user_data(request.user)
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats_view(request):
    tasks = Task.objects.filter(user=request.user, is_deleted=False)
    total_completed = tasks.filter(completed=True).count()
    total_pending = tasks.filter(completed=False).count()

    # Generate heatmap dictionary format
    heatmap_data = {}
    completed_tasks = tasks.filter(completed=True, completed_at__isnull=False)
    for task in completed_tasks:
        # Convert to user timezone/date format YYYY-MM-DD
        date_str = task.completed_at.strftime("%Y-%m-%d")
        heatmap_data[date_str] = heatmap_data.get(date_str, 0) + 1

    return Response({
        "total_completed": total_completed,
        "total_pending": total_pending,
        "heatmap_data": heatmap_data
    })

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def tasks_view(request):
    if request.method == "GET":
        tasks = Task.objects.filter(user=request.user, is_deleted=False).order_index = 0
        # Order by completed asc, and then by priority high/medium/low, then by created_at desc
        # Let's do python sorting to keep it clean and robust
        tasks_list = list(Task.objects.filter(user=request.user, is_deleted=False))
        
        priority_map = {"High": 0, "Medium": 1, "Low": 2}
        tasks_list.sort(key=lambda t: (t.completed, priority_map.get(t.priority, 2), -(t.created_at.timestamp() if t.created_at else 0)))

        data = [{
            "id": t.id,
            "title": t.title,
            "completed": t.completed,
            "priority": t.priority,
            "created_at": t.created_at,
            "completed_at": t.completed_at
        } for t in tasks_list]
        return Response(data)

    elif request.method == "POST":
        title = request.data.get("title")
        priority = request.data.get("priority", "Low")

        if not title:
            return Response({"error": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.create(
            user=request.user,
            title=title,
            priority=priority
        )
        return Response({
            "id": task.id,
            "title": task.title,
            "completed": task.completed,
            "priority": task.priority
        }, status=status.HTTP_201_CREATED)

@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def task_detail_view(request, pk):
    try:
        task = Task.objects.get(pk=pk, user=request.user, is_deleted=False)
    except Task.DoesNotExist:
        return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "PATCH":
        completed = request.data.get("completed")
        title = request.data.get("title")
        priority = request.data.get("priority")

        if completed is not None:
            task.completed = completed
            if completed:
                task.completed_at = timezone.now()
            else:
                task.completed_at = None
        if title is not None:
            task.title = title
        if priority is not None:
            task.priority = priority

        task.save()
        return Response({
            "id": task.id,
            "title": task.title,
            "completed": task.completed,
            "priority": task.priority
        })

    elif request.method == "DELETE":
        task.is_deleted = True
        task.save()
        return Response({"success": "Task deleted successfully."})
