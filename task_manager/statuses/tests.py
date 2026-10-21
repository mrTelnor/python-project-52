from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from task_manager.statuses.models import Status

# Хранилище без манифеста: тесты не зависят от collectstatic.
STORAGES_WITHOUT_MANIFEST = {
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

NOT_LOGGED_IN = 'Вы не авторизованы! Пожалуйста, выполните вход.'


@override_settings(STORAGES=STORAGES_WITHOUT_MANIFEST)
class StatusTestCase(TestCase):
    fixtures = ['users.json', 'statuses.json']

    def login(self):
        self.client.force_login(User.objects.get(username='tyrion'))


class StatusListTest(StatusTestCase):
    def setUp(self):
        self.url = reverse('statuses_index')

    def test_list_shows_statuses(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for status in Status.objects.all():
            self.assertContains(response, status.name)
        self.assertContains(response, 'Создать статус')

    def test_list_requires_login(self):
        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)


class StatusCreateTest(StatusTestCase):
    def setUp(self):
        self.url = reverse('status_create')

    def test_form_has_standard_field(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'id="id_name"')

    def test_create(self):
        self.login()

        response = self.client.post(self.url, {'name': 'завершен'}, follow=True)

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertContains(response, 'Статус успешно создан')
        self.assertTrue(Status.objects.filter(name='завершен').exists())

    def test_duplicate_name(self):
        self.login()

        response = self.client.post(self.url, {'name': 'новый'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.assertEqual(Status.objects.filter(name='новый').count(), 1)

    def test_create_requires_login(self):
        response = self.client.post(self.url, {'name': 'завершен'}, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)
        self.assertFalse(Status.objects.filter(name='завершен').exists())


class StatusUpdateTest(StatusTestCase):
    def setUp(self):
        self.status = Status.objects.get(name='новый')
        self.url = reverse('status_update', args=[self.status.pk])

    def test_update(self):
        self.login()

        response = self.client.post(self.url, {'name': 'открыт'}, follow=True)

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertContains(response, 'Статус успешно изменен')
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'открыт')

    def test_update_to_existing_name(self):
        self.login()

        response = self.client.post(self.url, {'name': 'в работе'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'новый')

    def test_update_requires_login(self):
        response = self.client.post(self.url, {'name': 'открыт'}, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)
        self.status.refresh_from_db()
        self.assertEqual(self.status.name, 'новый')


class StatusDeleteTest(StatusTestCase):
    def setUp(self):
        self.status = Status.objects.get(name='новый')
        self.url = reverse('status_delete', args=[self.status.pk])

    def test_delete_page_asks_confirmation(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())

    def test_delete(self):
        self.login()

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertContains(response, 'Статус успешно удален')
        self.assertFalse(Status.objects.filter(pk=self.status.pk).exists())

    def test_delete_requires_login(self):
        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())


class StatusInUseDeleteTest(StatusTestCase):
    fixtures = ['users.json', 'statuses.json', 'tasks.json']

    def test_delete_status_in_use_forbidden(self):
        # Статус «новый» назначен задаче из tasks.json.
        status = Status.objects.get(name='новый')
        self.login()

        response = self.client.post(
            reverse('status_delete', args=[status.pk]), follow=True
        )

        self.assertRedirects(response, reverse('statuses_index'))
        self.assertContains(
            response, 'Невозможно удалить статус, потому что он используется'
        )
        self.assertNotContains(response, 'Статус успешно удален')
        self.assertTrue(Status.objects.filter(pk=status.pk).exists())
