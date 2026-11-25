from rest_framework import serializers

from ..models import Video


class VideoList(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'thumbnail_url', 'category')