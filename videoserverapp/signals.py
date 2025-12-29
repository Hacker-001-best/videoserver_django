import os
from urllib.parse import urlparse
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import video


@receiver(post_delete, sender=video)
def delete_video_file(sender, instance, **kwargs):
    if not instance.video_path:
        return

    url = instance.video_path

    # если это URL — разбираем
    if url.startswith('http://') or url.startswith('https://'):
        parsed = urlparse(url)
        relative_path = parsed.path  # /uploads/123_video.mp4
    else:
        relative_path = url

    # убираем MEDIA_URL
    if relative_path.startswith(settings.MEDIA_URL):
        relative_path = relative_path.replace(settings.MEDIA_URL, '', 1)

    abs_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    if os.path.isfile(abs_path):
        try:
            os.remove(abs_path)
            print(f"Файл удалён: {abs_path}")
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")
    else:
        print(f"Файл не найден: {abs_path}")
