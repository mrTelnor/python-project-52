from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from task_manager.mixins import AuthorRequiredMixin, AuthRequiredMixin
from task_manager.tasks.forms import TaskForm
from task_manager.tasks.models import Task


class TaskListView(AuthRequiredMixin, ListView):
    queryset = Task.objects.select_related(
        'status', 'author', 'executor'
    ).order_by('id')
    template_name = 'tasks/index.html'
    context_object_name = 'tasks'


class TaskDetailView(AuthRequiredMixin, DetailView):
    queryset = Task.objects.select_related(
        'status', 'author', 'executor'
    ).prefetch_related('labels')
    template_name = 'tasks/detail.html'
    context_object_name = 'task'


class TaskCreateView(AuthRequiredMixin, SuccessMessageMixin, CreateView):
    form_class = TaskForm
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Task successfully created')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskUpdateView(AuthRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Task successfully updated')


class TaskDeleteView(
    AuthRequiredMixin, AuthorRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks_index')
    success_message = _('Task successfully deleted')
    author_required_message = _('A task can only be deleted by its author')
    author_required_url = 'tasks_index'
