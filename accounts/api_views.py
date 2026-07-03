from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Task, Profile

@api_view(['POST'])
@permission_classes([AllowAny])
def register_api(request):
    username = request.data.get('username')
    password = request.data.get('password')
    image = request.FILES.get('image')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': f"Username '{username}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    profile, created = Profile.objects.get_or_create(user=user)
    if image:
        profile.image = image
        profile.save()

    token, _ = Token.objects.get_or_create(user=user)
    
    image_url = profile.image.url if profile.image else None

    return Response({
        'token': token.key,
        'user': {
            'username': user.username,
            'image_url': image_url
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        try:
            profile = user.profile
            image_url = profile.image.url if profile.image else None
        except Profile.DoesNotExist:
            image_url = None

        return Response({
            'token': token.key,
            'user': {
                'username': user.username,
                'image_url': image_url
            }
        })
    else:
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    request.user.auth_token.delete()
    return Response({'success': 'Logged out successfully.'})

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create_api(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user, is_deleted=False).order_by('completed', '-created_at')
        task_data = []
        for task in tasks:
            task_data.append({
                'id': task.id,
                'title': task.title,
                'completed': task.completed,
                'priority': task.priority,
                'created_at': task.created_at,
                'completed_at': task.completed_at
            })
        return Response(task_data)

    elif request.method == 'POST':
        title = request.data.get('title')
        priority = request.data.get('priority', 'Low')
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.create(user=request.user, title=title, priority=priority)
        return Response({
            'id': task.id,
            'title': task.title,
            'completed': task.completed,
            'priority': task.priority
        }, status=status.HTTP_201_CREATED)

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail_api(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user)
    
    if request.method == 'PATCH':
        title = request.data.get('title')
        priority = request.data.get('priority')
        completed = request.data.get('completed')

        if title is not None:
            task.title = title
        if priority is not None:
            task.priority = priority
        if completed is not None:
            task.completed = completed
            if completed:
                task.completed_at = timezone.now()
            else:
                task.completed_at = None

        task.save()
        return Response({
            'id': task.id,
            'title': task.title,
            'completed': task.completed,
            'priority': task.priority
        })

    elif request.method == 'DELETE':
        task.is_deleted = True
        task.save()
        return Response({'success': 'Task deleted successfully.'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats_api(request):
    # Total completed (lifetime)
    total_completed = Task.objects.filter(user=request.user, completed=True).count()
    # Total pending
    total_pending = Task.objects.filter(user=request.user, completed=False, is_deleted=False).count()

    # Heatmap data
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
        'total_completed': total_completed,
        'total_pending': total_pending,
        'heatmap_data': heatmap_data
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_api(request):
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'Please choose an image to upload.'}, status=status.HTTP_400_BAD_REQUEST)

    profile, created = Profile.objects.get_or_create(user=request.user)
    profile.image = image
    profile.save()

    image_url = profile.image.url if profile.image else None

    return Response({
        'success': 'Profile photo updated successfully!',
        'user': {
            'username': request.user.username,
            'image_url': image_url
        }
    })
