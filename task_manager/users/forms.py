from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from task_manager.forms import TailwindFormMixin


class UserCreateForm(TailwindFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # В модели имя и фамилия необязательные, в формах — обязательные.
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        # Как в демо: фокус на первом поле, а не на username.
        self.fields['username'].widget.attrs.pop('autofocus', None)
        self.fields['first_name'].widget.attrs['autofocus'] = True


class UserUpdateForm(UserCreateForm):
    def clean_username(self):
        """Проверка уникальности без учёта редактируемого пользователя.

        В UserCreationForm.clean_username self.instance не исключается,
        поэтому неизменённый username давал бы ошибку «уже существует».
        """
        username = self.cleaned_data.get('username')
        duplicates = User.objects.filter(username__iexact=username).exclude(
            pk=self.instance.pk
        )
        if username and duplicates.exists():
            self._update_errors(
                ValidationError(
                    {
                        'username': self.instance.unique_error_message(
                            User, ['username']
                        )
                    }
                )
            )
        else:
            return username
