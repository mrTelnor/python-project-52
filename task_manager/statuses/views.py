from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.mixins import AuthRequiredMixin, ProtectedDeleteMixin
from task_manager.statuses.forms import StatusForm
from task_manager.statuses.models import Status


class StatusListView(AuthRequiredMixin, ListView):
    queryset = Status.objects.order_by('id')
    template_name = 'statuses/index.html'
    context_object_name = 'statuses'


class StatusCreateView(AuthRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = StatusForm
    template_name = 'statuses/create.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully created')


class StatusUpdateView(AuthRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully updated')


class StatusDeleteView(
    AuthRequiredMixin, ProtectedDeleteMixin, SuccessMessageMixin, DeleteView
):
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses_index')
    success_message = _('Status successfully deleted')
    protected_message = _('Cannot delete status because it is in use')
