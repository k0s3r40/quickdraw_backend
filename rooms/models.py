from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    p_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('player 1'))
    p_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('player 2'))
    p_1_shoot_ts = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('player 1 shoot ts'))
    p_2_shoot_ts = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('player 2 shoot ts'))
    winner = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('winner'))

    @property
    def has_empty_space(self):
        return not all([self.p_1, self.p_2])

