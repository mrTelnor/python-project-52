from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class AuthRequiredMixin(LoginRequiredMixin):
    """Неавторизованного отправляет на страницу входа с флеш-сообщением."""

    def handle_no_permission(self):
        messages.error(
            self.request, _('You are not logged in! Please log in.')
        )
        return redirect(settings.LOGIN_URL)


class UserSelfRequiredMixin:
    """Изменять и удалять учётную запись может только её владелец.

    Ставится после AuthRequiredMixin: сюда доходит только вошедший
    пользователь.
    """

    def dispatch(self, request, *args, **kwargs):
        if self.get_object() != request.user:
            messages.error(
                request, _('You do not have permission to change this user.')
            )
            return redirect('users_index')
        return super().dispatch(request, *args, **kwargs)


class AuthorRequiredMixin:
    """Действие над объектом доступно только его автору.

    Ставится после AuthRequiredMixin. В представлении задаются
    author_required_message и author_required_url.
    """

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            messages.error(request, self.author_required_message)
            return redirect(self.author_required_url)
        return super().dispatch(request, *args, **kwargs)
