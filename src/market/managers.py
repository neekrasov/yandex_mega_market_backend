from django.core.exceptions import ObjectDoesNotExist
from django.db.models import manager


class UnitManager(manager.Manager):
    def get_unit_or_none(self, **extra_fields):
        try:
            unit = self.model.objects.get(**extra_fields)
        except ObjectDoesNotExist:
            unit = None
        return unit
