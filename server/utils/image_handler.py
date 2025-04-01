import os
from django.conf import settings

def save_image(file, folder='uploads'):
    """
    Save an uploaded image to the local filesystem.
    In the future, this can be extended to upload to S3 or other storage solutions.
    """
    upload_dir = os.path.join(settings.MEDIA_ROOT, folder)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return os.path.join(settings.MEDIA_URL, folder, file.name)
