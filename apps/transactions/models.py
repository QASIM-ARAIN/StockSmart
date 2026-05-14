from django.db import models
from apps.accounts.models import User
from apps.products.models import Product, Supplier

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    OUT_REASONS = [
        ('sold', 'Sold'),
        ('damaged', 'Damaged/Expired'),
        ('internal', 'Internal Use'),
        ('other', 'Other'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    out_reason = models.CharField(max_length=20, choices=OUT_REASONS, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.product.name} ({self.quantity})"