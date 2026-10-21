from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.forms import TailwindFormMixin
from task_manager.statuses.models import Status


class StatusForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Status
        fields = ('name',)
        # Встроенное «Статус с таким Имя уже существует.» звучит не по-русски.
        error_messages = {
            'name': {'unique': _('A status with this name already exists.')},
        }
