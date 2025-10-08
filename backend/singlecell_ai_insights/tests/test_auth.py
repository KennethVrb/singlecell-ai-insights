from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


class AuthEndpointTests(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            username='tester',
            password='strong-pass',
            email='tester@example.com',
        )

    def test_login_sets_cookies_for_valid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'strong-pass'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(
            response.data['user']['email'],
            'tester@example.com',
        )

        access_cookie = settings.SIMPLE_JWT['AUTH_COOKIE']
        refresh_cookie = settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
        self.assertIn(access_cookie, response.cookies)
        self.assertIn(refresh_cookie, response.cookies)
        self.assertEqual(
            response.cookies[access_cookie]['path'],
            settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        self.assertTrue(response.cookies[access_cookie]['httponly'])
        self.assertEqual(
            response.cookies[refresh_cookie]['path'],
            settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_PATH'],
        )
        self.assertTrue(response.cookies[refresh_cookie]['httponly'])

    def test_login_denies_invalid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        access_cookie = settings.SIMPLE_JWT['AUTH_COOKIE']
        refresh_cookie = settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
        self.assertNotIn(access_cookie, response.cookies)
        self.assertNotIn(refresh_cookie, response.cookies)

    def test_refresh_uses_cookie_and_rotates_tokens(self):
        self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'strong-pass'},
            format='json',
        )

        refresh_response = self.client.post(
            '/api/auth/refresh/',
            {},
            format='json',
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response.data, {'detail': 'refreshed'})

        access_cookie = settings.SIMPLE_JWT['AUTH_COOKIE']
        refresh_cookie = settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']
        self.assertIn(access_cookie, refresh_response.cookies)
        self.assertIn(refresh_cookie, refresh_response.cookies)

    def test_logout_requires_auth_and_clears_cookies(self):
        access_cookie = settings.SIMPLE_JWT['AUTH_COOKIE']
        refresh_cookie = settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE']

        self.client.post(
            '/api/auth/login/',
            {'username': 'tester', 'password': 'strong-pass'},
            format='json',
        )
        self.assertIn(access_cookie, self.client.cookies)
        self.assertIn(refresh_cookie, self.client.cookies)

        logout_response = self.client.post(
            '/api/auth/logout/',
            {},
            format='json',
        )
        self.assertEqual(
            logout_response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertIn(access_cookie, logout_response.cookies)
        self.assertIn(refresh_cookie, logout_response.cookies)
        self.assertEqual(
            logout_response.cookies[access_cookie]['path'],
            settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        self.assertEqual(
            logout_response.cookies[refresh_cookie]['path'],
            settings.SIMPLE_JWT['AUTH_REFRESH_COOKIE_PATH'],
        )
        self.assertEqual(
            int(logout_response.cookies[access_cookie]['max-age']),
            0,
        )
        self.assertEqual(
            int(logout_response.cookies[refresh_cookie]['max-age']),
            0,
        )
