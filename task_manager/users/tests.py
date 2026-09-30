from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

# Пароль всех пользователей из фикстуры users.json.
PASSWORD = 'test-pass'

# Хранилище без манифеста: тесты не зависят от collectstatic.
STORAGES_WITHOUT_MANIFEST = {
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}


@override_settings(STORAGES=STORAGES_WITHOUT_MANIFEST)
class UserTestCase(TestCase):
    fixtures = ['users.json']


class UserListTest(UserTestCase):
    def test_list_is_public_and_shows_users(self):
        response = self.client.get(reverse('users_index'))

        self.assertEqual(response.status_code, 200)
        for user in User.objects.all():
            self.assertContains(response, user.username)
            self.assertContains(response, user.get_full_name())


class UserCreateTest(UserTestCase):
    def setUp(self):
        self.url = reverse('user_create')
        self.data = {
            'first_name': 'Sansa',
            'last_name': 'Stark',
            'username': 'sansa',
            'password1': 'abc',
            'password2': 'abc',
        }

    def test_form_has_standard_fields(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for name in ('first_name', 'last_name', 'username',
                     'password1', 'password2'):
            self.assertContains(response, f'name="{name}"')
            self.assertContains(response, f'id="id_{name}"')

    def test_create_redirects_to_login(self):
        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, 'Пользователь успешно зарегистрирован')
        user = User.objects.get(username='sansa')
        self.assertEqual(user.get_full_name(), 'Sansa Stark')
        self.assertTrue(user.check_password('abc'))

    def test_duplicate_username(self):
        self.data['username'] = 'tyrion'

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.assertEqual(User.objects.filter(username='tyrion').count(), 1)


class LoginLogoutTest(UserTestCase):
    def test_login_redirects_to_index(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'tyrion', 'password': PASSWORD},
            follow=True,
        )

        self.assertRedirects(response, reverse('index'))
        self.assertContains(response, 'Вы залогинены')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username='tyrion', password=PASSWORD)

        response = self.client.post(reverse('logout'), follow=True)

        self.assertRedirects(response, reverse('index'))
        self.assertContains(response, 'Вы разлогинены')
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class UserUpdateTest(UserTestCase):
    def setUp(self):
        self.user = User.objects.get(username='tyrion')
        self.other = User.objects.get(username='arya')
        self.data = {
            'first_name': 'Tyrion',
            'last_name': 'Lannister-Updated',
            'username': 'tyrion',
            'password1': 'new',
            'password2': 'new',
        }

    def test_update_self(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('user_update', args=[self.user.pk]), self.data, follow=True
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertContains(response, 'Пользователь успешно изменен')
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, 'Lannister-Updated')
        self.assertTrue(self.user.check_password('new'))
        # После смены пароля пользователь остаётся залогинен.
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_update_other_user_forbidden(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('user_update', args=[self.other.pk]),
            {**self.data, 'username': 'arya'},
            follow=True,
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertContains(response, 'У вас нет прав для изменения')
        self.other.refresh_from_db()
        self.assertEqual(self.other.last_name, 'Stark')

    def test_update_requires_login(self):
        response = self.client.get(
            reverse('user_update', args=[self.user.pk]), follow=True
        )

        self.assertRedirects(response, reverse('login'))
        self.assertContains(
            response, 'Вы не авторизованы! Пожалуйста, выполните вход.'
        )


class UserDeleteTest(UserTestCase):
    def setUp(self):
        self.user = User.objects.get(username='tyrion')
        self.other = User.objects.get(username='arya')

    def test_delete_self(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('user_delete', args=[self.user.pk]), follow=True
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertContains(response, 'Пользователь успешно удален')
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_delete_other_user_forbidden(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('user_delete', args=[self.other.pk]), follow=True
        )

        self.assertRedirects(response, reverse('users_index'))
        self.assertContains(response, 'У вас нет прав для изменения')
        self.assertTrue(User.objects.filter(pk=self.other.pk).exists())

    def test_delete_requires_login(self):
        response = self.client.post(
            reverse('user_delete', args=[self.user.pk]), follow=True
        )

        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
