from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Task, Category
from django.utils import timezone
from datetime import timedelta


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            user=self.user,
            due_date=timezone.now() + timedelta(days=1)
        )
        self.task.categories.add(self.category)

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertTrue(isinstance(self.category.id, str))
        self.assertEqual(len(self.category.id), 64)

    def test_task_creation(self):
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.user, self.user)
        self.assertEqual(self.task.categories.count(), 1)
        self.assertTrue(isinstance(self.task.id, str))
        self.assertEqual(len(self.task.id), 64)


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name='Test Category')
        self.task_data = {
            'title': 'API Test Task',
            'description': 'API Test Description',
            'due_date': (timezone.now() + timedelta(days=1)).isoformat(),
            'categories': [self.category.id]
        }

    def test_create_task(self):
        response = self.client.post('/api/tasks/', self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.get().title, 'API Test Task')

    def test_get_tasks(self):
        Task.objects.create(title='Test Task', user=self.user)
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_task(self):
        task = Task.objects.create(title='Old Title', user=self.user)
        response = self.client.put(f'/api/tasks/{task.id}/', {'title': 'New Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.get(id=task.id).title, 'New Title')

    def test_delete_task(self):
        task = Task.objects.create(title='To Be Deleted', user=self.user)
        response = self.client.delete(f'/api/tasks/{task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.login_data = {
            'username': 'testuser',
            'password': '12345'
        }

    def test_jwt_auth(self):
        response = self.client.post('/api/token/', self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_use_jwt_token(self):
        auth_response = self.client.post('/api/token/', self.login_data, format='json')
        token = auth_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ThrottlingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)

    def test_throttling(self):
        for _ in range(15):
            response = self.client.get('/api/tasks/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)