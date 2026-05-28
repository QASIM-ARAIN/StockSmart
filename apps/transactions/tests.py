from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.factory import UserFactory
from apps.products.models import Product, Category, Supplier
from apps.transactions.models import Transaction
from apps.transactions.factory import TransactionFactory

class TransactionFactoryTest(TestCase):

    def setUp(self):
        self.admin = UserFactory.create_admin('admin1', 'admin123', 'admin@test.com')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            unit='pieces',
            minimum_threshold=5,
            current_stock=0,
            created_by=self.admin
        )

    def test_stock_in_increases_product_stock(self):
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=50,
            user=self.admin
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 50)

    def test_stock_out_decreases_product_stock(self):
        self.product.current_stock = 50
        self.product.save()
        TransactionFactory.create_stock_out(
            product=self.product,
            quantity=20,
            user=self.admin
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 30)

    def test_stock_out_raises_error_when_insufficient_stock(self):
        self.product.current_stock = 10
        self.product.save()
        with self.assertRaises(ValueError):
            TransactionFactory.create_stock_out(
                product=self.product,
                quantity=20,
                user=self.admin
            )

    def test_stock_in_creates_transaction_record(self):
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=50,
            user=self.admin
        )
        self.assertEqual(Transaction.objects.filter(
            product=self.product,
            transaction_type='IN'
        ).count(), 1)

    def test_stock_out_creates_transaction_record(self):
        self.product.current_stock = 50
        self.product.save()
        TransactionFactory.create_stock_out(
            product=self.product,
            quantity=20,
            user=self.admin
        )
        self.assertEqual(Transaction.objects.filter(
            product=self.product,
            transaction_type='OUT'
        ).count(), 1)

    def test_stock_out_zero_quantity_raises_error(self):
        self.product.current_stock = 50
        self.product.save()
        with self.assertRaises(Exception):
            TransactionFactory.create_stock_out(
                product=self.product,
                quantity=0,
                user=self.admin
            )

    def test_stock_in_with_supplier(self):
        supplier = Supplier.objects.create(name='Test Supplier')
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=50,
            user=self.admin,
            supplier=supplier
        )
        transaction = Transaction.objects.get(product=self.product)
        self.assertEqual(transaction.supplier, supplier)

    def test_transaction_records_performed_by_user(self):
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=50,
            user=self.admin
        )
        transaction = Transaction.objects.get(product=self.product)
        self.assertEqual(transaction.performed_by, self.admin)

    def test_stock_cannot_go_negative(self):
        self.product.current_stock = 10
        self.product.save()
        with self.assertRaises(ValueError):
            TransactionFactory.create_stock_out(
                product=self.product,
                quantity=11,
                user=self.admin
            )
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 10)


class TransactionViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = UserFactory.create_admin('admin1', 'admin123', 'admin@test.com')
        self.staff = UserFactory.create_staff('staff1', 'staff123', 'staff@test.com')
        self.staff.status = 'active'
        self.staff.save()
        self.product = Product.objects.create(
            name='Laptop',
            unit='pieces',
            minimum_threshold=5,
            current_stock=50,
            created_by=self.admin
        )

    def test_transaction_list_loads(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)

    def test_stock_in_page_loads(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('stock_in'))
        self.assertEqual(response.status_code, 200)

    def test_stock_out_page_loads(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('stock_out'))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_record_stock_in(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.post(reverse('stock_in'), {
            'product': self.product.pk,
            'quantity': 10,
        })
        self.assertRedirects(response, reverse('transaction_list'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 60)

    def test_staff_can_record_stock_out(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.post(reverse('stock_out'), {
            'product': self.product.pk,
            'quantity': 10,
            'out_reason': 'sold'
        })
        self.assertRedirects(response, reverse('transaction_list'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.current_stock, 40)

    def test_stock_out_with_insufficient_quantity_shows_error(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.post(reverse('stock_out'), {
            'product': self.product.pk,
            'quantity': 1000,
            'out_reason': 'sold'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Insufficient stock')

    def test_stock_in_with_zero_quantity_shows_error(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.post(reverse('stock_in'), {
            'product': self.product.pk,
            'quantity': 0,
        })
        self.assertEqual(response.status_code, 200)

    def test_transaction_filter_by_type(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('transaction_list'), {'type': 'IN'})
        self.assertEqual(response.status_code, 200)