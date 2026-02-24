from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class DashboardTests(TestCase):
    def setUp(self):
        # create a regular student user and a company user
        self.student = User.objects.create_user(username='stud', email='stud@example.com', password='pass', user_type='user')
        self.company = User.objects.create_user(username='comp', email='comp@example.com', password='pass', user_type='company')
        self.client = Client()

    def test_student_dashboard_contains_new_keys(self):
        self.client.login(username='stud', password='pass')
        res = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(res.status_code, 200)
        ctx = res.context
        # core stats
        self.assertIn('total_applications', ctx)
        # new feature keys
        self.assertIn('resume_count', ctx)
        self.assertIn('badges_count', ctx)
        self.assertIn('unread_notifications', ctx)
        self.assertIn('unread_chats', ctx)

    def test_company_dashboard_contains_new_keys(self):
        self.client.login(username='comp', password='pass')
        res = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(res.status_code, 200)
        ctx = res.context
        self.assertIn('total_posts', ctx)
        # new company keys
        self.assertIn('unread_notifications', ctx)
        self.assertIn('unread_chats', ctx)
