import os
import uuid
from django.utils.text import slugify


def params_to_ints(qs):
    return [int(str_id.strip()) for str_id in qs.split(",")]

def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join(instance.folder, filename)