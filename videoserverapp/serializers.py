from django.contrib.postgres import serializers
from .models import *
class VideoSerializer(serializers.ModelSerializer):
    model=video
    fields=('__all__')