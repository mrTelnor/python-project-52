from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.labels.forms import LabelForm
from task_manager.labels.models import Label
from task_manager.mixins import AuthRequiredMixin, ProtectedDeleteMixin


class LabelListView(AuthRequiredMixin, ListView):
    queryset = Label.objects.order_by('id')
    template_name = 'labels/index.html'
    context_object_name = 'labels'


class LabelCreateView(AuthRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = LabelForm
    template_name = 'labels/create.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Label successfully created')


class LabelUpdateView(AuthRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Label
    form_class = LabelForm
    template_name = 'labels/update.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Label successfully updated')


class LabelDeleteView(
    AuthRequiredMixin, ProtectedDeleteMixin, SuccessMessageMixin, DeleteView
):
    model = Label
    template_name = 'labels/delete.html'
    success_url = reverse_lazy('labels_index')
    success_message = _('Label successfully deleted')
    protected_message = _('Cannot delete label because it is in use')
