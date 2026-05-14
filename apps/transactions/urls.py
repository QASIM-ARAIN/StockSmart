from django.urls import path
from apps.transactions import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('stock-in/', views.stock_in, name='stock_in'),
    path('stock-out/', views.stock_out, name='stock_out'),
]