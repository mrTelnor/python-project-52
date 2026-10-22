from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.forms import TailwindFormMixin
from task_manager.labels.models import Label


class LabelForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Label
        fields = ('name',)
        # Встроенное «Метка с таким Имя уже существует.» звучит не по-русски.
        error_messages = {
            'name': {'unique': _('A label with this name already exists.')},
        }
