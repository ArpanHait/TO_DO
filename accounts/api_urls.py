from django.urls import path
from . import api_views

urlpatterns = [
    path('auth/register/', api_views.register_view, name='api_register'),
    path('auth/login/', api_views.login_view, name='api_login'),
    path('auth/logout/', api_views.logout_view, name='api_logout'),
    path('profile/update/', api_views.update_profile_view, name='api_update_profile'),
    path('stats/', api_views.stats_view, name='api_stats'),
    path('tasks/', api_views.tasks_view, name='api_tasks'),
    path('tasks/<int:pk>/', api_views.task_detail_view, name='api_task_detail'),
]
