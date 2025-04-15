from django.core.files.storage import FileSystemStorage
from django.conf import settings

class CKEditor5FileSystemStorage(FileSystemStorage):
    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.CKEDITOR_5_UPLOAD_PATH
        kwargs['base_url'] = settings.CKEDITOR_5_UPLOAD_URL
        super().__init__(*args, **kwargs)
