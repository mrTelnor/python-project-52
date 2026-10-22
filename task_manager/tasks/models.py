from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label
from task_manager.statuses.models import Status


class Task(models.Model):
    name = models.CharField(_('Name'), max_length=150, unique=True)
    description = models.TextField(_('Description'), blank=True)
    # PROTECT: статус и пользователя, связанных с задачей, удалить нельзя.
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name='tasks',
        verbose_name=_('Status'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_tasks',
        verbose_name=_('Author'),
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='executed_tasks',
        null=True,
        blank=True,
        verbose_name=_('Executor'),
    )
    labels = models.ManyToManyField(
        Label,
        through='TaskLabel',
        related_name='tasks',
        blank=True,
        verbose_name=_('Labels'),
    )
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return self.name


class TaskLabel(models.Model):
    """Связь задачи с меткой.

    Своя промежуточная таблица нужна ради PROTECT: в обычной связи
    «многие ко многим» удаление метки молча снимает её с задач.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('task', 'label'), name='unique_task_label'
            ),
        ]
