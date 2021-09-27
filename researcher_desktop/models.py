import logging

from functools import cached_property

from django.db import models
from django.conf import settings
from django.urls import reverse

from researcher_workspace import models as workspace_models
from vm_manager.utils.utils import get_nectar
from vm_manager.utils.utils import FlavorDetails


logger = logging.getLogger(__name__)


class DesktopType(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    name = models.CharField(max_length=128)
    description = models.TextField()
    logo = models.ImageField(blank=True)
    image_name = models.CharField(max_length=256)
    default_flavor_name = models.CharField(max_length=32)
    big_flavor_name = models.CharField(max_length=32)
    feature = models.ForeignKey(workspace_models.Feature,
                                on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True)

    @property
    def default_flavor(self):
        return self._flavor_map[self.default_flavor_name]

    @property
    def big_flavor(self):
        return self._flavor_map[self.big_flavor_name]

    @cached_property
    def _flavor_map(self):
        res = {}
        for f in get_nectar().nova.flavors.list():
            res[f.name] = FlavorDetails(f)
        return res

    @cached_property
    def source_volume_id(self):
        return get_nectar().cinder.volumes.list(
            search_opts={'name': self.image_name})[0].id

    @property
    def security_groups(self):
        # FIX ME - this possibly shouldn't be hardwired
        return settings.OS_SECGROUPS
