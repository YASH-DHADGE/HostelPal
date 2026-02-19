from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from django.db import connection

class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.username = 'testuser'
        self.password = 'testpass123'
        self.existing_user = User.objects.create_user(username='existinguser', password='existingpass123')

    def test_register_happy_path(self):
        response = self.client.post(self.register_url, {
            'username': self.username,
            'password1': self.password,
            'password2': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username=self.username).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Account created successfully')

    def test_register_username_already_exists(self):
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'password1': self.password,
            'password2': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Username already exists')

    def test_register_passwords_do_not_match(self):
        response = self.client.post(self.register_url, {
            'username': self.username,
            'password1': self.password,
            'password2': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertFalse(User.objects.filter(username=self.username).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Passwords do not match')

    def test_register_get_request(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.home_url = reverse('home')
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_happy_path(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid username or password')

    def test_login_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistentuser',
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invalid username or password')

    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_home_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_unauthenticated_user(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

class RawSqlExampleViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.raw_sql_url = reverse('raw_sql_example')
        self.username = 'john'
        self.password = 'password123'
        self.email = 'john@example.com'

    def test_raw_sql_example_operations(self):
        response = self.client.get(self.raw_sql_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'raw_sql_example.html')

        # Verify user was created
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM auth_user WHERE username = %s", [self.username])
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], self.username)

        # Verify user data in context
        self.assertIn('user_data', response.context)
        user_data = response.context['user_data']
        self.assertEqual(user_data['username'], self.username)

        # Verify email was updated
        with connection.cursor() as cursor:
            cursor.execute("SELECT email FROM auth_user WHERE username = %s", [self.username])
            row = cursor.fetchone()
            self.assertEqual(row[0], self.email)

        # Verify user was deleted
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM auth_user WHERE username = %s", [self.username])
            row = cursor.fetchone()
            self.assertIsNone(row)

    def test_raw_sql_example_no_side_effects_on_multiple_calls(self):
        # First call
        self.client.get(self.raw_sql_url)

        # Second call should not fail (user already deleted)
        response = self.client.get(self.raw_sql_url)
        self.assertEqual(response.status_code, 200)

        # Verify no user exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT username FROM auth_user WHERE username = %s", [self.username])
            row = cursor.fetchone()
            self.assertIsNone(row)