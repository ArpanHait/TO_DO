from django.urls import path
from . import api_views

urlpatterns = [
    path('auth/register/', api_views.register_api, name='api_register'),
    path('auth/login/', api_views.login_api, name='api_login'),
    path('auth/logout/', api_views.logout_api, name='api_logout'),
    path('tasks/', api_views.task_list_create_api, name='api_task_list_create'),
    path('tasks/<int:pk>/', api_views.task_detail_api, name='api_task_detail'),
    path('stats/', api_views.stats_api, name='api_stats'),
    path('profile/update/', api_views.update_profile_api, name='api_update_profile'),
]
