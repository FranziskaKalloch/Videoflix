from rest_framework import serializers

from ..models import Video


class VideoListSerializer(serializers.ModelSerializer):
    ''' Serialize video metadata for the video list endpoint. '''
    class Meta:
        model = Video
        fields = ('id', 'title', 'description', 'thumbnail_url', 'category', 'created_at')
        
