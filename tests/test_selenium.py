from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apps.accounts.factory import UserFactory
from apps.products.models import Product, Category
from apps.transactions.factory import TransactionFactory


class AuthSeleniumTest(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=Service('chromedriver.exe'))
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.admin = UserFactory.create_admin(
            username='seleniumadmin',
            password='admin123',
            email='selenium@admin.com'
        )
        self.staff = UserFactory.create_staff(
            username='seleniumstaff',
            password='staff123',
            email='selenium@staff.com'
        )
        self.staff.status = 'active'
        self.staff.save()

    def tearDown(self):
        self.driver.quit()

    def login(self, username, password):
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys(username)
        self.driver.find_element(By.NAME, 'password').send_keys(password)
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)

    def test_home_page_loads(self):
        self.driver.get(self.live_server_url)
        self.assertIn('StockSmart', self.driver.title)
        login_btn = self.driver.find_element(By.LINK_TEXT, 'Login')
        self.assertTrue(login_btn.is_displayed())

    def test_register_link_on_home_page(self):
        self.driver.get(self.live_server_url)
        self.driver.find_element(By.LINK_TEXT, 'Register').click()
        self.assertIn('register', self.driver.current_url)

    def test_valid_admin_login(self):
        self.login('seleniumadmin', 'admin123')
        self.wait.until(EC.url_contains('dashboard'))
        self.assertIn('dashboard', self.driver.current_url)

    def test_invalid_login_shows_error(self):
        self.login('wronguser', 'wrongpass')
        error = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert'))
        )
        self.assertIn('Invalid', error.text)

    def test_pending_staff_cannot_login(self):
        UserFactory.create_staff('pendingstaff', 'staff123', 'pending@test.com')
        self.login('pendingstaff', 'staff123')
        error = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert'))
        )
        self.assertIn('pending', error.text.lower())

    def test_logout_redirects_to_login(self):
        self.login('seleniumadmin', 'admin123')
        self.wait.until(EC.url_contains('dashboard'))
        self.driver.find_element(By.LINK_TEXT, 'Logout').click()
        self.wait.until(EC.url_contains('login'))
        self.assertIn('login', self.driver.current_url)

    def test_registration_with_mismatched_passwords(self):
        self.driver.get(f'{self.live_server_url}/register/')
        self.driver.find_element(By.NAME, 'username').send_keys('testuser')
        self.driver.find_element(By.NAME, 'email').send_keys('test@test.com')
        self.driver.find_element(By.NAME, 'password').send_keys('pass123')
        self.driver.find_element(By.NAME, 'confirm_password').send_keys('different')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        error = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert'))
        )
        self.assertIn('Passwords do not match', error.text)


class ProductSeleniumTest(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=Service('chromedriver.exe'))
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.admin = UserFactory.create_admin(
            'prodadmin', 'admin123', 'prod@admin.com'
        )
        self.category = Category.objects.create(name='Electronics')

    def tearDown(self):
        self.driver.quit()

    def login_as_admin(self):
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys('prodadmin')
        self.driver.find_element(By.NAME, 'password').send_keys('admin123')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.wait.until(EC.url_contains('dashboard'))

    def test_admin_can_access_products_page(self):
        self.login_as_admin()
        self.driver.find_element(By.LINK_TEXT, 'Products').click()
        self.wait.until(EC.url_contains('products'))
        self.assertIn('products', self.driver.current_url)

    def test_admin_can_add_product(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/products/add/')
        self.driver.find_element(By.NAME, 'name').send_keys('Test Laptop')
        self.driver.find_element(By.NAME, 'unit').send_keys('pieces')
        self.driver.find_element(By.NAME, 'minimum_threshold').clear()
        self.driver.find_element(By.NAME, 'minimum_threshold').send_keys('5')
        self.driver.find_element(By.NAME, 'current_stock').send_keys('20')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.wait.until(EC.url_contains('products'))
        self.assertTrue(Product.objects.filter(name='Test Laptop').exists())

    def test_product_appears_in_list(self):
        Product.objects.create(
            name='Visible Product',
            unit='pieces',
            minimum_threshold=5,
            current_stock=20,
            created_by=self.admin
        )
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/products/')
        self.assertIn('Visible Product', self.driver.page_source)

    def test_product_search(self):
        Product.objects.create(
            name='SearchableItem',
            unit='pieces',
            minimum_threshold=5,
            current_stock=20,
            created_by=self.admin
        )
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/products/')
        search_box = self.driver.find_element(By.NAME, 'search')
        search_box.send_keys('SearchableItem')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.assertIn('SearchableItem', self.driver.page_source)


class TransactionSeleniumTest(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=Service('chromedriver.exe'))
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.admin = UserFactory.create_admin(
            'txadmin', 'admin123', 'tx@admin.com'
        )
        self.product = Product.objects.create(
            name='Test Product',
            unit='pieces',
            minimum_threshold=5,
            current_stock=50,
            created_by=self.admin
        )

    def tearDown(self):
        self.driver.quit()

    def login_as_admin(self):
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys('txadmin')
        self.driver.find_element(By.NAME, 'password').send_keys('admin123')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.wait.until(EC.url_contains('dashboard'))

    def test_stock_in_page_loads(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/transactions/stock-in/')
        self.assertIn('Stock In', self.driver.page_source)

    def test_stock_out_page_loads(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/transactions/stock-out/')
        self.assertIn('Stock Out', self.driver.page_source)

    def test_admin_can_record_stock_in(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/transactions/stock-in/')
        from selenium.webdriver.support.ui import Select
        Select(self.driver.find_element(By.NAME, 'product')).select_by_visible_text(
            'Test Product (Current: 50 pieces)'
        )
        self.driver.find_element(By.NAME, 'quantity').send_keys('10')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.wait.until(EC.url_contains('transactions'))
        self.assertIn('Test Product', self.driver.page_source)

    def test_transaction_appears_in_history(self):
        TransactionFactory.create_stock_in(
            product=self.product,
            quantity=25,
            user=self.admin
        )
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/transactions/')
        self.assertIn('Test Product', self.driver.page_source)


class ReportsSeleniumTest(LiveServerTestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=Service('chromedriver.exe'))
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 10)
        self.admin = UserFactory.create_admin(
            'repadmin', 'admin123', 'rep@admin.com'
        )

    def tearDown(self):
        self.driver.quit()

    def login_as_admin(self):
        self.driver.get(f'{self.live_server_url}/login/')
        self.driver.find_element(By.NAME, 'username').send_keys('repadmin')
        self.driver.find_element(By.NAME, 'password').send_keys('admin123')
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type=submit]')
        self.driver.execute_script("arguments[0].click();", submit_btn)
        self.wait.until(EC.url_contains('dashboard'))

    def test_reports_page_loads(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/reports/')
        self.assertIn('Reports', self.driver.page_source)

    def test_dashboard_shows_stats(self):
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/dashboard/')
        self.assertIn('Total Products', self.driver.page_source)
        self.assertIn('Low Stock Alerts', self.driver.page_source)

    def test_low_stock_alert_on_dashboard(self):
        Product.objects.create(
            name='Low Item',
            unit='pieces',
            minimum_threshold=10,
            current_stock=3,
            created_by=self.admin
        )
        self.login_as_admin()
        self.driver.get(f'{self.live_server_url}/dashboard/')
        self.assertIn('Low Item', self.driver.page_source)