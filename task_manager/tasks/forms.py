from django import forms

from task_manager.forms import TailwindFormMixin
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
