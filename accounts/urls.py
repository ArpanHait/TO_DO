from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-task/<int:id>/', views.delete_task, name='delete_task'),
    path('undo-delete-task/<int:id>/', views.undo_delete_task, name='undo_delete_task'),
    path('complete-task/<int:id>/', views.complete_task, name='complete_task'),
    path('edit-task/<int:id>/', views.edit_task, name='edit_task'),
    path('update-profile/', views.update_profile, name='update_profile'),
]