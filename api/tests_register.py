from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User

class UserRegistrationTests(APITestCase):
    def test_user_registration(self):
        url = reverse('register')
        data = {'username': 'newuser', 'password': 'newpassword', 'email': 'new@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
