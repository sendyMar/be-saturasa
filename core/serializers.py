from rest_framework import serializers
from .models import Template, Song

class TemplateSerializer(serializers.ModelSerializer):
    idTheme = serializers.CharField(source='id_theme')
    usedCount = serializers.IntegerField(source='used_count')

    class Meta:
        model = Template
        fields = ['idTheme', 'name', 'usedCount', 'category', 'path']

class SongSerializer(serializers.ModelSerializer):
    idSong = serializers.CharField(source='id_song')

    class Meta:
        model = Song
        fields = ['idSong', 'name', 'singer', 'category', 'path']
