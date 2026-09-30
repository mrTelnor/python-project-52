from django.contrib.auth.forms import AuthenticationForm


class TailwindFormMixin:
    """Добавляет полям формы классы Tailwind."""

    input_class = 'block w-full border-gray-500 px-3 py-2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = self.input_class


class LoginForm(TailwindFormMixin, AuthenticationForm):
    pass
