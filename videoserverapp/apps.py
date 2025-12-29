from django.apps import AppConfig


class VideoserverappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videoserverapp'

    def ready(self):
        import videoserverapp.signals