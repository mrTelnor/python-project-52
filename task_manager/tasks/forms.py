from django import forms
from django.contrib.auth.models import User

from task_manager.forms import TailwindFormMixin
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task


class UserChoiceField(forms.ModelChoiceField):
    """Пользователь в списке выбора — по имени и фамилии, как в демо."""

    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


class TaskForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Task
        fields = ('name', 'description', 'status', 'executor')
        field_classes = {'executor': UserChoiceField}
        widgets = {'description': forms.Textarea(attrs={'rows': 10})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Без order_by порядок в списках выбора зависит от БД.
        self.fields['status'].queryset = Status.objects.order_by('id')
        self.fields['executor'].queryset = User.objects.order_by(
            'first_name', 'last_name'
        )
