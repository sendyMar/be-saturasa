from rest_framework import viewsets, mixins
from .models import Template, Song
from .serializers import TemplateSerializer, SongSerializer

class TemplateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows templates to be viewed.
    """
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    permission_classes = [] # Allow public access for now, or adjust as needed

class SongViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = []
