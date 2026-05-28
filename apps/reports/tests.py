from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.factory import UserFactory
from apps.products.models import Product, Category
from apps.transactions.factory import TransactionFactory

class ReportsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = UserFactory.create_admin('admin1', 'admin123', 'admin@test.com')
        self.staff = UserFactory.create_staff('staff1', 'staff123', 'staff@test.com')
        self.staff.status = 'active'
        self.staff.save()
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            category=self.category,
            unit='pieces',
            minimum_threshold=10,
            current_stock=0,
            created_by=self.admin
        )

    def test_reports_page_loads_for_admin(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)

    def test_reports_page_loads_for_staff(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_user_cannot_access_reports(self):
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 302)

    def test_low_stock_product_appears_in_reports(self):
        self.product.current_stock = 5
        self.product.save()
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertContains(response, 'Laptop')

    def test_total_stock_in_calculated_correctly(self):
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=50,
            user=self.admin
        )
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=30,
            user=self.admin
        )
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertContains(response, '80')

    def test_total_stock_out_calculated_correctly(self):
        self.product.current_stock = 100
        self.product.save()
        TransactionFactory.create_stock_out(
            product=self.product,
            quantity=30,
            user=self.admin
        )
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertContains(response, '30')

    def test_low_stock_count_is_correct(self):
        self.product.current_stock = 5
        self.product.save()
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.context['low_stock_count'], 1)

    def test_no_low_stock_when_all_products_above_threshold(self):
        self.product.current_stock = 50
        self.product.save()
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.context['low_stock_count'], 0)