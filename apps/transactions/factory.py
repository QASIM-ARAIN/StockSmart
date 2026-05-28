from apps.transactions.models import Transaction
from apps.products.models import Product

class TransactionFactory:

    @staticmethod
    def create_stock_in(product, quantity, user, supplier=None, notes=None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        transaction = Transaction.objects.create(
            product=product,
            transaction_type='IN',
            quantity=quantity,
            performed_by=user,
            supplier=supplier,
            notes=notes
        )
        product.current_stock += quantity
        product.save()
        return transaction

    @staticmethod
    def create_stock_out(product, quantity, user, out_reason=None, notes=None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if quantity > product.current_stock:
            raise ValueError("Insufficient stock available")
        transaction = Transaction.objects.create(
            product=product,
            transaction_type='OUT',
            quantity=quantity,
            performed_by=user,
            out_reason=out_reason,
            notes=notes
        )
        product.current_stock -= quantity
        product.save()
        return transaction