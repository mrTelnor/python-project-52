from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

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
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')

    def __str__(self):
        return self.name
