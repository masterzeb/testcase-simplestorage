import os
import sys

from django.conf import settings
from django.db.models import Model, ImageField, CharField, BooleanField


class Storage(Model):
    mount_point = CharField(max_length=100)
    is_mounted = BooleanField(default=False)
    is_overloaded = BooleanField(default=False)

    @property
    def free_space_kb(self):
        stat = os.statvfs(os.path.join(settings.MEDIA_ROOT, self.mount_point))
        return (stat.f_bsize * stat.f_bavail / 1024)

    @classmethod
    def get_storages(cls, update=True):
        if update:
            cls.update_storages()
        storages = cls.objects.filter(is_overloaded=False, is_mounted=True)
        return sorted({st.mount_point: st.free_space_kb for st in storages})

    @classmethod
    def update_storages(cls):
        for mount_point in os.listdir(settings.MEDIA_ROOT):
            try:
                storage = cls.objects.get(mount_point=mount_point)
            except cls.DoesNotExist:
                storage = cls(mount_point=mount_point)

            # TODO: check perms
            storage.is_overloaded = storage.free_space_kb < settings.STORAGE_MIN_SPACE_KB
            storage.is_mounted = True
            storage.save()

        cls.objects \
            .exclude(mount_point__in=os.listdir(settings.MEDIA_ROOT)) \
            .update(is_mounted=False)

    @classmethod
    def make_path(cls, obj, filename):
        pk_str = str(obj.pk)
        prefix_length = len(str(sys.maxint)) - len(pk_str)
        if prefix_length > 0:
            pk_str = '0' * prefix_length + pk_str
        path = os.path.join(cls.get_storages()[0], pk_str[-2:], pk_str[-4:-2], pk_str[:-4])
        path += os.path.splitext(filename)[-1]
        return path

    def __unicode__(self):
        return self.mount_point


class Image(Model):
    file = ImageField(upload_to=Storage.make_path, blank=True, null=True)
    content_type = CharField(max_length=100, blank=True, null=True)
    deleted = BooleanField(default=False)

    @property
    def is_file_exist(self):
        return self.file and os.path.exists(self.file.path)
