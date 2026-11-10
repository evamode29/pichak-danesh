import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateHomeworkStorage(FileSystemStorage):
    """Store homework files outside the web document root."""

    def __init__(self, location=None, base_url=None, **kwargs):
        if location is None:
            location = os.path.join(str(settings.BASE_DIR), "private_homework_media")
        super().__init__(location=location, base_url=base_url, **kwargs)
