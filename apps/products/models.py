from django.contrib.auth.models import AbstractUser
from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_purchases(self):
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(
            supplier=self,
            transaction_type='IN'
        ).count()

    def total_quantity_supplied(self):
        from apps.transactions.models import Transaction
        result = Transaction.objects.filter(
            supplier=self,
            transaction_type='IN'
        )
        return sum(t.quantity for t in result)

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=50)
    minimum_threshold = models.PositiveIntegerField(default=10)
    current_stock = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.current_stock <= self.minimum_threshold