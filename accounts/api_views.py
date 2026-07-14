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

from django.db.models.functions import TruncDate
from django.db.models import Case, Count, IntegerField, Value, When

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def stats_view(request):
    tasks = Task.objects.filter(user=request.user, is_deleted=False)
    total_completed = Task.objects.filter(user=request.user, completed=True).count()
    total_pending = tasks.filter(completed=False).count()

    # Aggregating task completions by day to render the Github-style Heatmap Calendar
    # NOTE: This intentionally does NOT filter out 'is_deleted', natively preserving historical Heatmap data forever!
    completed_counts = (
        Task.objects.filter(user=request.user, completed=True, completed_at__isnull=False)
        .annotate(date=TruncDate('completed_at'))
        .values('date')
        .annotate(count=Count('id'))
    )

    heatmap_data = {
        obj['date'].strftime('%Y-%m-%d'): obj['count']
        for obj in completed_counts if obj['date']
    }

    return Response({
        "total_completed": total_completed,
        "total_pending": total_pending,
        "heatmap_data": heatmap_data
    })


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def tasks_view(request):
    if request.method == "GET":
        # Order by completed asc, and then by priority high/medium/low, then by created_at desc
        priority_order = Case(
            When(priority="High", then=Value(0)),
            When(priority="Medium", then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        )
        tasks = Task.objects.filter(user=request.user, is_deleted=False).order_by(
            "completed", priority_order, "-created_at"
        )

        data = [{
            "id": t.id,
            "title": t.title,
            "completed": t.completed,
            "priority": t.priority,
            "created_at": t.created_at,
            "completed_at": t.completed_at
        } for t in tasks]
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
