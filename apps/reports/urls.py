from django.urls import path
from apps.reports import views

urlpatterns = [
    path('', views.reports_view, name='reports'),
]