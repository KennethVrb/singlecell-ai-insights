from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthEndpointTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username='tester', password='strong-pass'
        )

    def test_login_returns_tokens_for_valid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'strong-pass'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_denies_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'strong-pass'},
            format='json',
        )
        refresh_token = login_response.data['refresh']

        refresh_response = self.client.post(
            '/api/auth/refresh/',
            {'refresh': refresh_token},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
