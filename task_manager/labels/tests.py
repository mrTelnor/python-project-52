from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from task_manager.labels.models import Label

# Хранилище без манифеста: тесты не зависят от collectstatic.
STORAGES_WITHOUT_MANIFEST = {
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

NOT_LOGGED_IN = 'Вы не авторизованы! Пожалуйста, выполните вход.'


@override_settings(STORAGES=STORAGES_WITHOUT_MANIFEST)
class LabelTestCase(TestCase):
    fixtures = ['users.json', 'labels.json']

    def login(self):
        self.client.force_login(User.objects.get(username='tyrion'))

    def assert_requires_login(self, response):
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)


class LabelListTest(LabelTestCase):
    def setUp(self):
        self.url = reverse('labels_index')

    def test_list_shows_labels(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for label in Label.objects.all():
            self.assertContains(response, label.name)
        self.assertContains(response, 'Создать метку')
        self.assertContains(response, 'Изменить')
        self.assertContains(response, 'Удалить')

    def test_list_requires_login(self):
        response = self.client.get(self.url, follow=True)

        self.assert_requires_login(response)


class LabelCreateTest(LabelTestCase):
    def setUp(self):
        self.url = reverse('label_create')

    def test_form_has_standard_field(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'id="id_name"')
        self.assertContains(response, '>Имя:</label>')

    def test_create(self):
        self.login()

        response = self.client.post(self.url, {'name': 'дизайн'}, follow=True)

        self.assertRedirects(response, reverse('labels_index'))
        self.assertContains(response, 'Метка успешно создана')
        self.assertTrue(Label.objects.filter(name='дизайн').exists())

    def test_duplicate_name(self):
        self.login()

        response = self.client.post(self.url, {'name': 'ошибка'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Метка с таким именем уже существует.')
        self.assertEqual(Label.objects.filter(name='ошибка').count(), 1)

    def test_create_requires_login(self):
        response = self.client.post(self.url, {'name': 'дизайн'}, follow=True)

        self.assert_requires_login(response)
        self.assertFalse(Label.objects.filter(name='дизайн').exists())


class LabelUpdateTest(LabelTestCase):
    def setUp(self):
        self.label = Label.objects.get(name='фича')
        self.url = reverse('label_update', args=[self.label.pk])

    def test_update(self):
        self.login()

        response = self.client.post(
            self.url, {'name': 'улучшение'}, follow=True
        )

        self.assertRedirects(response, reverse('labels_index'))
        self.assertContains(response, 'Метка успешно изменена')
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'улучшение')

    def test_update_to_existing_name(self):
        self.login()

        response = self.client.post(self.url, {'name': 'ошибка'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'фича')

    def test_update_requires_login(self):
        response = self.client.post(
            self.url, {'name': 'улучшение'}, follow=True
        )

        self.assert_requires_login(response)
        self.label.refresh_from_db()
        self.assertEqual(self.label.name, 'фича')


class LabelDeleteTest(LabelTestCase):
    def setUp(self):
        self.label = Label.objects.get(name='фича')
        self.url = reverse('label_delete', args=[self.label.pk])

    def test_delete_page_asks_confirmation(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())

    def test_delete(self):
        self.login()

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, reverse('labels_index'))
        self.assertContains(response, 'Метка успешно удалена')
        self.assertFalse(Label.objects.filter(pk=self.label.pk).exists())

    def test_delete_requires_login(self):
        response = self.client.post(self.url, follow=True)

        self.assert_requires_login(response)
        self.assertTrue(Label.objects.filter(pk=self.label.pk).exists())


class LabelAccessTest(LabelTestCase):
    def test_forms_require_login(self):
        for name, args in (
            ('label_create', []),
            ('label_update', [1]),
            ('label_delete', [1]),
        ):
            with self.subTest(name):
                response = self.client.get(
                    reverse(name, args=args), follow=True
                )

                self.assert_requires_login(response)

    def test_missing_label_not_found(self):
        self.login()
        for name in ('label_update', 'label_delete'):
            with self.subTest(name):
                response = self.client.get(reverse(name, args=[999]))

                self.assertEqual(response.status_code, 404)


class LabelInUseDeleteTest(LabelTestCase):
    fixtures = ['users.json', 'statuses.json', 'labels.json', 'tasks.json']

    def test_delete_label_in_use_forbidden(self):
        # Метка «ошибка» стоит на задаче из tasks.json.
        label = Label.objects.get(name='ошибка')
        self.login()

        response = self.client.post(
            reverse('label_delete', args=[label.pk]), follow=True
        )

        self.assertRedirects(response, reverse('labels_index'))
        self.assertContains(
            response, 'Невозможно удалить метку, потому что она используется'
        )
        self.assertNotContains(response, 'Метка успешно удалена')
        self.assertTrue(Label.objects.filter(pk=label.pk).exists())
