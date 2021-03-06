from django.db import models
from django.utils.translation import ugettext_lazy as _
from safedelete.models import SafeDeleteModel


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Time created"))
    modified_at = models.DateTimeField(auto_now=True, verbose_name=_("Time modified"))

    class Meta:
        abstract = True


class TimeStampedSafeDeleteModel(TimeStampedModel, SafeDeleteModel):
    class Meta:
        abstract = True


class NameModel(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name
