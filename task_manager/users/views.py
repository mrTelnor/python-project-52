from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.mixins import AuthRequiredMixin, UserSelfRequiredMixin
from task_manager.users.forms import UserCreateForm, UserUpdateForm


class UserListView(ListView):
    queryset = User.objects.order_by('id')
    template_name = 'users/index.html'
    context_object_name = 'users'


class UserCreateView(SuccessMessageMixin, CreateView):
    form_class = UserCreateForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('login')
    success_message = _('User successfully registered')


class UserUpdateView(
    AuthRequiredMixin, UserSelfRequiredMixin, SuccessMessageMixin, UpdateView
):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users_index')
    success_message = _('User successfully updated')

    def form_valid(self, form):
        response = super().form_valid(form)
        # После смены пароля пользователь остаётся залогинен.
        update_session_auth_hash(self.request, self.object)
        return response


class UserDeleteView(
    AuthRequiredMixin, UserSelfRequiredMixin, SuccessMessageMixin, DeleteView
):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users_index')
    success_message = _('User successfully deleted')
