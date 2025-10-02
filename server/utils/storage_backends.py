"""
Storage backends for handling media files.
Supports local filesystem (development) and S3 (production).
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Storage backend for media files in production (S3).
    Only used when USE_S3 is True in settings.
    """
    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'
