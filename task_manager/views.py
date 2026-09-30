from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from task_manager.forms import LoginForm


def index(request):
    return render(request, 'index.html')


class UserLoginView(SuccessMessageMixin, LoginView):
    form_class = LoginForm
    template_name = 'login.html'
    success_message = _('You are logged in')


class UserLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        messages.info(request, _('You are logged out'))
        return super().post(request, *args, **kwargs)
