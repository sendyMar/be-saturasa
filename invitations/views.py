from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import InvitationData
from .serializers import InvitationDataSerializer

class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # LAZY DELETION: Cek expired setiap kali user mengakses list/invitation
        from django.utils import timezone
        now = timezone.now()
        
        # Hapus undangan yang sudah lewat masa aktif
        InvitationData.objects.filter(user=self.request.user, expires_at__lt=now).delete()
        
        # Users can only see their own invitations
        return InvitationData.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Auto-assign user
        serializer.save(user=self.request.user)
