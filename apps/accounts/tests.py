from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.accounts.factory import UserFactory

class UserModelTest(TestCase):
    
    def setUp(self):
        self.admin = UserFactory.create_admin(
            username='testadmin',
            password='admin123',
            email='admin@test.com'
        )
        self.staff = UserFactory.create_staff(
            username='teststaff',
            password='staff123',
            email='staff@test.com'
        )

    # --- Model Tests ---

    def test_admin_role_is_set_correctly(self):
        self.assertEqual(self.admin.role, 'admin')

    def test_staff_role_is_set_correctly(self):
        self.assertEqual(self.staff.role, 'staff')

    def test_staff_status_is_pending_by_default(self):
        self.assertEqual(self.staff.status, 'pending')

    def test_admin_status_is_active_by_default(self):
        self.assertEqual(self.admin.status, 'active')

    def test_is_admin_returns_true_for_admin(self):
        self.assertTrue(self.admin.is_admin())

    def test_is_admin_returns_false_for_staff(self):
        self.assertFalse(self.staff.is_admin())

    def test_is_staff_member_returns_true_for_staff(self):
        self.assertTrue(self.staff.is_staff_member())


class LoginViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = UserFactory.create_admin(
            username='loginadmin',
            password='admin123',
            email='loginadmin@test.com'
        )
        self.staff = UserFactory.create_staff(
            username='loginstaff',
            password='staff123',
            email='loginstaff@test.com'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_valid_admin_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginadmin',
            'password': 'admin123'
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_invalid_password_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginadmin',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_invalid_username_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'nonexistent',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')

    def test_pending_staff_cannot_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'loginstaff',
            'password': 'staff123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pending')

    def test_logout_redirects_to_login(self):
        self.client.login(username='loginadmin', password='admin123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='loginadmin', password='admin123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('dashboard'))


class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_valid_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'pass123',
            'confirm_password': 'pass123',
            'role': 'staff'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_with_mismatched_passwords(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser2',
            'email': 'newuser2@test.com',
            'password': 'pass123',
            'confirm_password': 'different123',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')

    def test_registration_with_duplicate_username(self):
        UserFactory.create_staff('existinguser', 'pass123', 'existing@test.com')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'new@test.com',
            'password': 'pass123',
            'confirm_password': 'pass123',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username already exists')

    def test_registration_with_missing_fields(self):
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': '',
            'password': '',
            'confirm_password': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All fields are required')

    def test_registration_with_short_password(self):
        response = self.client.post(reverse('register'), {
            'username': 'shortpass',
            'email': 'short@test.com',
            'password': '123',
            'confirm_password': '123',
            'role': 'staff'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'at least 6 characters')


class AccessControlTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin = UserFactory.create_admin('admin1', 'admin123', 'admin1@test.com')
        self.staff = UserFactory.create_staff('staff1', 'staff123', 'staff1@test.com')
        self.staff.status = 'active'
        self.staff.save()

    def test_unauthenticated_user_redirected_from_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_staff_cannot_access_user_list(self):
        self.client.login(username='staff1', password='staff123')
        response = self.client.get(reverse('user_list'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_admin_can_access_user_list(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_approve_user(self):
        self.client.login(username='admin1', password='admin123')
        response = self.client.get(reverse('approve_user', args=[self.staff.pk]))
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.status, 'active')

    def test_admin_can_reject_user(self):
        new_staff = UserFactory.create_staff('newstaff', 'pass123', 'new@test.com')
        self.client.login(username='admin1', password='admin123')
        self.client.get(reverse('reject_user', args=[new_staff.pk]))
        new_staff.refresh_from_db()
        self.assertEqual(new_staff.status, 'rejected')