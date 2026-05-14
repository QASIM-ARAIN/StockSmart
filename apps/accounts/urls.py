from django.urls import path
from apps.accounts import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/approve/<int:pk>/', views.approve_user_view, name='approve_user'),
    path('users/reject/<int:pk>/', views.reject_user_view, name='reject_user'),
]