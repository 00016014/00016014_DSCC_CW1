import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task, Category, Tag


class TestAuthentication(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

    def test_dashboard_loads_when_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)


class TestTasks(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.category = Category.objects.create(
            name='Work',
            color='#6366f1',
            user=self.user
        )
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            priority='high',
            status='todo',
            author=self.user,
            category=self.category
        )

    def test_task_list_loads(self):
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)

    def test_task_detail_loads(self):
        response = self.client.get(reverse('task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)

    def test_task_create_loads(self):
        response = self.client.get(reverse('task_create'))
        self.assertEqual(response.status_code, 200)

    def test_task_can_be_created(self):
        response = self.client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'New Description',
            'priority': 'medium',
            'status': 'todo',
            'category': self.category.pk,
        })
        self.assertEqual(Task.objects.count(), 2)

    def test_task_can_be_deleted(self):
        response = self.client.post(
            reverse('task_delete', args=[self.task.pk])
        )
        self.assertEqual(Task.objects.count(), 0)


class TestCategories(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_category_page_loads(self):
        response = self.client.get(reverse('category_list'))
        self.assertEqual(response.status_code, 200)

    def test_category_can_be_created(self):
        response = self.client.post(reverse('category_list'), {
            'name': 'Personal',
            'color': '#10b981'
        })
        self.assertEqual(Category.objects.count(), 1)