from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.transactions.models import Transaction

@receiver(post_save, sender=Transaction)
def check_low_stock(sender, instance, **kwargs):
    product = instance.product
    if product.is_low_stock():
        print(f"WARNING: {product.name} is low on stock ({product.current_stock} remaining)")