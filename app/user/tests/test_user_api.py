from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    # Test the users api public

    def setUP(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # Test creating with valid payload is successful
        payload = {
            "email": "test@test.com",
            "password": "test123",
            "name": "test user"
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exist(self):
        # Test creating a user that already exists failed
        payload = {
            "email": "test@test.com",
            "password": "test123",
            "name": "lololo"
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # Test that the password must be more than 5 characters
        payload = {
            "email": "test@test.com",
            "password": "te"
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        # Test a token is created for the user
        payload = {'email': 'test@test.com', 'password': 'test123'}
        create_user(**payload)

        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        # Test if token is not created if credentials are invalid
        create_user(email="test@test.com", password="test123")
        payload = {'email': 'test@test.com', 'password': 'test1234'}
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # Test if token is not created if user is not existed
        payload = {'email': 'test@test.com', 'password': 'test123'}
        response = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_fields(self):
        # Test email and password are required for creating token
        response = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
