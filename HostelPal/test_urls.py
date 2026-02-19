from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

class AdminURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')

    def test_admin_url_accessible(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "HostelPal Warden Login")

    def test_admin_site_header(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "HostelPal Warden Login")

    def test_admin_site_title(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "Welcome Warden")

    def test_admin_site_url(self):
        response = self.client.get('/admin/')
        self.assertContains(response, 'href="/warden"')

    def test_admin_index_title(self):
        response = self.client.get('/admin/')
        self.assertContains(response, "Hello Warden")

class PasswordResetURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_password_reset_url_accessible(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset.html')

    def test_password_reset_post_valid_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'test@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver')

    def test_password_reset_post_invalid_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'nonexistent@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_done_url_accessible(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset_done.html')

    def test_password_reset_confirm_url_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset_confirm.html')

    def test_password_reset_confirm_url_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = 'invalid-token'
        response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The password reset link was invalid")

    def test_password_reset_complete_url_accessible(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset_complete.html')

class WardenPasswordResetURLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.warden = User.objects.create_user(
            username='warden',
            email='warden@example.com',
            password='testpass123'
        )

    def test_warden_password_reset_url_accessible(self):
        response = self.client.get(reverse('warden_password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warden/password_reset.html')

    def test_warden_password_reset_post_valid_email(self):
        response = self.client.post(
            reverse('warden_password_reset'),
            {'email': 'warden@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/wardens/password_reset/done/')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver')
        self.assertTemplateUsed(mail.outbox[0], 'warden/password_reset_email.html')

    def test_warden_password_reset_post_invalid_email(self):
        response = self.client.post(
            reverse('warden_password_reset'),
            {'email': 'nonexistent@example.com'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_warden_password_reset_done_url_accessible(self):
        response = self.client.get(reverse('warden_password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warden/password_reset_done.html')

    def test_warden_password_reset_confirm_url_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.warden.pk))
        token = default_token_generator.make_token(self.warden)
        response = self.client.get(
            reverse('warden_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warden/password_reset_confirm.html')

    def test_warden_password_reset_confirm_url_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.warden.pk))
        token = 'invalid-token'
        response = self.client.get(
            reverse('warden_password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The password reset link was invalid")

    def test_warden_password_reset_complete_url_accessible(self):
        response = self.client.get(reverse('warden_password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'warden/password_reset_complete.html')

class HomeURLIncludeTests(TestCase):
    def test_home_url_included(self):
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 404)

    def test_nonexistent_url_returns_404(self):
        response = self.client.get('/nonexistent-url/')
        self.assertEqual(response.status_code, 404)