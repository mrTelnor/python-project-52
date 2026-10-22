import django_filters
from django.contrib.auth.models import User
from django.forms import CheckboxInput
from django.utils.translation import gettext_lazy as _
from django_filters.fields import ModelChoiceField

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.forms import UserChoiceField
from task_manager.tasks.models import Task


class ExecutorChoiceField(UserChoiceField, ModelChoiceField):
    """Исполнитель в фильтре — по имени и фамилии, как в форме задачи."""


class ExecutorFilter(django_filters.ModelChoiceFilter):
    field_class = ExecutorChoiceField


class TaskFilter(django_filters.FilterSet):
    # pr-10 оставляет место под стрелку списка: с px-3 текст наезжает на неё.
    select_class = 'min-w-48 border-gray-500 py-2 pl-3 pr-10'

    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.order_by('id'),
        label=_('Status'),
        empty_label=_('Not selected'),
    )
    executor = ExecutorFilter(
        queryset=User.objects.order_by('first_name', 'last_name'),
        label=_('Executor'),
        empty_label=_('Not selected'),
    )
    labels = django_filters.ModelChoiceFilter(
        queryset=Label.objects.order_by('id'),
        label=_('Label'),
        empty_label=_('Not selected'),
    )
    self_tasks = django_filters.BooleanFilter(
        label=_('Only own tasks'),
        widget=CheckboxInput,
        method='filter_self_tasks',
    )

    class Meta:
        model = Task
        fields = ('status', 'executor', 'labels', 'self_tasks')

    @property
    def form(self):
        form = super().form
        for name in ('status', 'executor', 'labels'):
            form.fields[name].widget.attrs['class'] = self.select_class
        return form

    def filter_self_tasks(self, queryset, name, value):
        # Неотмеченный чекбокс приходит как False — фильтр не применяем.
        if not value:
            return queryset
        return queryset.filter(author=self.request.user)
