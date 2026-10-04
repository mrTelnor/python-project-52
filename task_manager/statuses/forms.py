from django import forms

from task_manager.forms import TailwindFormMixin
from task_manager.statuses.models import Status


class StatusForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Status
        fields = ('name',)
