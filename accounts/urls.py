from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-task/<int:id>/', views.delete_task, name='delete_task'),
    path('complete-task/<int:id>/', views.complete_task, name='complete_task'),
]