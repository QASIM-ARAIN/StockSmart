from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.factory import UserFactory
from apps.products.models import Product, Category, Supplier

class CategoryModelTest(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(name='Electronics')
        self.assertEqual(category.name, 'Electronics')

    def test_category_str(self):
        category = Category.objects.create(name='Electronics')
        self.assertEqual(str(category), 'Electronics')

    def test_duplicate_category_not_allowed(self):
        Category.objects.create(name='Electronics')
        with self.assertRaises(Exception):
            Category.objects.create(name='Electronics')


class ProductModelTest(TestCase):

    def setUp(self):
        self.admin = UserFactory.create_admin('admin1', 'admin123', 'admin@test.com')
        self.category = Category.objects.create(name='Electronics')

    def test_product_creation(self):
        product = Product.objects.create(
            name='Laptop',
            category=self.category,
            unit='pieces',
            minimum_threshold=5,
            current_stock=20,
            created_by=self.admin
        )
        self.assertEqual(product.name, 'Laptop')
        self.assertEqual(product.current_stock, 20)

    def test_product_str(self):
        product = Product.objects.create(
            name='Laptop',
            unit='pieces',
            minimum_threshold=5,
            current_stock=20,
            created_by=self.admin
        )
        self.assertEqual(str(product), 'Laptop')

    def test_is_low_stock_returns_true_when_below_threshold(self):
        product = Product.objects.create(
            name='Mouse',
            unit='pieces',
            minimum_threshold=10,
            current_stock=5,
            created_by=self.admin
        )
        self.assertTrue(product.is_low_stock())

    def test_is_low_stock_returns_false_when_above_threshold(self):
        product = Product.objects.create(
            name='Keyboard',
            unit='pieces',
            minimum_threshold=10,
            current_stock=50,
            created_by=self.admin
        )
        self.assertFalse(product.is_low_stock())

    def test_is_low_stock_returns_true_when_equal_to_threshold(self):
        product = Product.objects.create(
            name='Monitor',
            unit='pieces',
            minimum_threshold=10,
            current_stock=10,
            created_by=self.admin
        )
        self.assertTrue(product.is_low_stock())

    def test_product_without_category(self):
        product = Product.objects.create(
            name='Generic Item',
            unit='pieces',
            minimum_threshold=5,
            current_stock=10,
            created_by=self.admin
        )
        self.assertIsNone(product.category)


class ProductViewTest(TestCase):

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
            minimum_threshold=5,
            current_stock=20,
            created_by=self.admin
        )

    def test_product_list_loads_for_admin(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_loads_for_staff(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.get(reverse('product_list'))
        self.assertEqual(response.status_code, 200)

    def test_staff_cannot_access_add_product(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.get(reverse('product_add'))
        self.assertRedirects(response, reverse('product_list'))

    def test_admin_can_add_product(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.post(reverse('product_add'), {
            'name': 'New Product',
            'category': self.category.pk,
            'unit': 'pieces',
            'minimum_threshold': 5,
            'current_stock': 10
        })
        self.assertTrue(Product.objects.filter(name='New Product').exists())

    def test_admin_can_edit_product(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.post(reverse('product_edit', args=[self.product.pk]), {
            'name': 'Updated Laptop',
            'unit': 'pieces',
            'minimum_threshold': 5,
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Laptop')

    def test_staff_cannot_delete_product(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.post(reverse('product_delete', args=[self.product.pk]))
        self.assertRedirects(response, reverse('product_list'))
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_admin_can_delete_product(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.post(reverse('product_delete', args=[self.product.pk]))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_product_search_returns_correct_results(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('product_list'), {'search': 'Laptop'})
        self.assertContains(response, 'Laptop')

    def test_product_filter_by_category(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('product_list'), {'category': self.category.pk})
        self.assertEqual(response.status_code, 200)


class SupplierModelTest(TestCase):

    def test_supplier_creation(self):
        supplier = Supplier.objects.create(
            name='Tech Supplies Co',
            phone='03001234567',
            email='tech@supplier.com'
        )
        self.assertEqual(supplier.name, 'Tech Supplies Co')

    def test_supplier_str(self):
        supplier = Supplier.objects.create(name='Tech Supplies Co')
        self.assertEqual(str(supplier), 'Tech Supplies Co')

    def test_supplier_optional_fields(self):
        supplier = Supplier.objects.create(name='Basic Supplier')
        self.assertIsNone(supplier.phone)
        self.assertIsNone(supplier.email)