from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from task_manager.labels.models import Label
from task_manager.tasks.models import Task, TaskLabel

# Хранилище без манифеста: тесты не зависят от collectstatic.
STORAGES_WITHOUT_MANIFEST = {
    **settings.STORAGES,
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

NOT_LOGGED_IN = 'Вы не авторизованы! Пожалуйста, выполните вход.'


@override_settings(STORAGES=STORAGES_WITHOUT_MANIFEST)
class TaskTestCase(TestCase):
    # Задача 1: автор tyrion, исполнитель jon, метки «ошибка» и «срочно».
    # Задача 2: автор arya, без меток.
    fixtures = ['users.json', 'statuses.json', 'labels.json', 'tasks.json']

    def setUp(self):
        self.tyrion = User.objects.get(username='tyrion')
        self.arya = User.objects.get(username='arya')
        self.jon = User.objects.get(username='jon')
        self.task = Task.objects.get(name='Написать отчёт')

    def login(self, user=None):
        self.client.force_login(user or self.tyrion)

    def assert_requires_login(self, response):
        self.assertRedirects(response, reverse('login'))
        self.assertContains(response, NOT_LOGGED_IN)


class TaskListTest(TaskTestCase):
    def test_list_shows_tasks(self):
        self.login()

        response = self.client.get(reverse('tasks_index'))

        self.assertEqual(response.status_code, 200)
        for task in Task.objects.all():
            self.assertContains(response, task.name)
            self.assertContains(response, task.status.name)
            self.assertContains(response, task.author.get_full_name())
        self.assertContains(response, self.jon.get_full_name())
        self.assertContains(response, 'Создать задачу')
        self.assertContains(response, 'Показать')
        self.assertContains(
            response, reverse('task_detail', args=[self.task.pk])
        )

    def test_list_requires_login(self):
        response = self.client.get(reverse('tasks_index'), follow=True)

        self.assert_requires_login(response)


class TaskDetailTest(TaskTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('task_detail', args=[self.task.pk])

    def test_detail_shows_task(self):
        self.login(self.arya)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.task.name)
        self.assertContains(response, self.task.description)
        self.assertContains(response, self.task.status.name)
        self.assertContains(response, self.tyrion.get_full_name())
        self.assertContains(response, self.jon.get_full_name())
        self.assertContains(response, 'Метки')
        for name in ('ошибка', 'срочно'):
            self.assertContains(response, name)
        self.assertNotContains(response, 'фича')

    def test_detail_requires_login(self):
        response = self.client.get(self.url, follow=True)

        self.assert_requires_login(response)


class TaskCreateTest(TaskTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('task_create')
        self.data = {
            'name': 'Собрать войско',
            'description': 'До зимы',
            'status': 1,
            'executor': self.arya.pk,
        }

    def test_form_has_standard_fields(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        for name in ('name', 'description', 'status', 'executor', 'labels'):
            self.assertContains(response, f'name="{name}"')
            self.assertContains(response, f'id="id_{name}"')
        # Исполнитель в списке выбора — по имени и фамилии.
        self.assertContains(response, f'>{self.jon.get_full_name()}</option>')
        self.assertContains(response, '>фича</option>')
        self.assertContains(response, 'multiple')
        for label in ('Имя', 'Описание', 'Статус', 'Исполнитель', 'Метки'):
            self.assertContains(response, f'>{label}:</label>')

    def test_form_empty_choice_in_russian(self):
        # В Django 6.1 пустой пункт — «- Select an option -» без перевода.
        self.login()

        response = self.client.get(self.url)

        self.assertContains(
            response, '<option value="" selected>Не выбрано</option>', count=2
        )
        self.assertNotContains(response, 'Select an option')

    def test_create_sets_author(self):
        self.login()

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertContains(response, 'Задача успешно создана')
        task = Task.objects.get(name='Собрать войско')
        self.assertEqual(task.author, self.tyrion)
        self.assertEqual(task.executor, self.arya)
        self.assertEqual(task.description, 'До зимы')

    def test_create_without_executor(self):
        self.login()
        self.data['executor'] = ''

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertIsNone(Task.objects.get(name='Собрать войско').executor)

    def test_create_with_labels(self):
        self.login()
        self.data['labels'] = [1, 2]

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        task = Task.objects.get(name='Собрать войско')
        self.assertQuerySetEqual(
            task.labels.order_by('pk'), ['ошибка', 'фича'], transform=str
        )

    def test_create_without_labels(self):
        self.login()

        self.client.post(self.url, self.data)

        task = Task.objects.get(name='Собрать войско')
        self.assertFalse(task.labels.exists())

    def test_duplicate_name(self):
        self.login()
        self.data['name'] = self.task.name

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Задача с таким именем уже существует.')
        self.assertEqual(Task.objects.filter(name=self.task.name).count(), 1)

    def test_create_requires_login(self):
        response = self.client.post(self.url, self.data, follow=True)

        self.assert_requires_login(response)
        self.assertFalse(Task.objects.filter(name='Собрать войско').exists())


class TaskUpdateTest(TaskTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('task_update', args=[self.task.pk])
        self.data = {
            'name': 'Написать отчёт к пятнице',
            'description': 'Квартальный отчёт',
            'status': 2,
            'executor': self.arya.pk,
        }

    def test_update_by_other_user(self):
        # Изменять задачу может любой вошедший пользователь, не только автор.
        self.login(self.arya)

        response = self.client.post(self.url, self.data, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertContains(response, 'Задача успешно изменена')
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Написать отчёт к пятнице')
        self.assertEqual(self.task.status.pk, 2)
        self.assertEqual(self.task.executor, self.arya)
        self.assertEqual(self.task.author, self.tyrion)

    def test_update_labels(self):
        self.login()
        self.data['labels'] = [2]

        self.client.post(self.url, self.data)

        self.assertQuerySetEqual(
            self.task.labels.all(), ['фича'], transform=str
        )

    def test_update_removes_all_labels(self):
        # Без выбранных меток поле labels в форме не отправляется.
        self.login()

        self.client.post(self.url, self.data)

        self.assertFalse(self.task.labels.exists())

    def test_update_form_shows_selected_labels(self):
        self.login()

        response = self.client.get(self.url)

        self.assertContains(response, '<option value="1" selected>ошибка')
        self.assertContains(response, '<option value="2">фича')

    def test_update_to_existing_name(self):
        self.login()
        self.data['name'] = 'Проверить стены'

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'уже существует')
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Написать отчёт')

    def test_update_requires_login(self):
        response = self.client.post(self.url, self.data, follow=True)

        self.assert_requires_login(response)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Написать отчёт')


class TaskDeleteTest(TaskTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('task_delete', args=[self.task.pk])

    def test_delete_page_asks_confirmation(self):
        self.login()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Да, удалить')

    def test_delete_by_author(self):
        self.login()

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertContains(response, 'Задача успешно удалена')
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
        # Метки остаются, удаляются только их связи с задачей.
        self.assertEqual(Label.objects.count(), 3)
        self.assertFalse(TaskLabel.objects.exists())

    def test_delete_by_not_author_forbidden(self):
        # jon — исполнитель задачи, но не автор.
        self.login(self.jon)

        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertContains(response, 'Задачу может удалить только ее автор')
        self.assertNotContains(response, 'Задача успешно удалена')
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())

    def test_delete_page_by_not_author_forbidden(self):
        self.login(self.arya)

        response = self.client.get(self.url, follow=True)

        self.assertRedirects(response, reverse('tasks_index'))
        self.assertContains(response, 'Задачу может удалить только ее автор')

    def test_delete_requires_login(self):
        response = self.client.post(self.url, follow=True)

        self.assert_requires_login(response)
        self.assertTrue(Task.objects.filter(pk=self.task.pk).exists())


class TaskAccessTest(TaskTestCase):
    def test_forms_require_login(self):
        for name, args in (
            ('task_create', []),
            ('task_update', [self.task.pk]),
            ('task_delete', [self.task.pk]),
        ):
            with self.subTest(name):
                response = self.client.get(
                    reverse(name, args=args), follow=True
                )

                self.assert_requires_login(response)

    def test_missing_task_not_found(self):
        self.login()
        for name in ('task_detail', 'task_update', 'task_delete'):
            with self.subTest(name):
                response = self.client.get(reverse(name, args=[999]))

                self.assertEqual(response.status_code, 404)
