from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from .models import Guest
from .serializers import GuestSerializer
from invitations.models import InvitationData, InvitationMember

class GuestViewSet(viewsets.ModelViewSet):
    serializer_class = GuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Allow if user is Owner OR Member
        queryset = Guest.objects.filter(
            Q(invitation__user=user) | Q(invitation__members__user=user)
        ).distinct()
        
        # Filter by invitation ID if provided
        invitation_id = self.request.query_params.get('invitation_id')
        if invitation_id:
            queryset = queryset.filter(invitation_id=invitation_id)
            
        return queryset.order_by('-name')

    def perform_create(self, serializer):
        # Ensure the invitation belongs to the user OR user is an editor/owner member
        invitation = serializer.validated_data.get('invitation')
        
        if not invitation:
             serializer.save()
             return

        # Check Owner
        is_owner = invitation.user == self.request.user
        # Check Member Role
        is_editor = invitation.members.filter(
            user=self.request.user, 
            role__in=['owner', 'editor']
        ).exists()

        if not (is_owner or is_editor):
            raise permissions.PermissionDenied("You do not have permission to add guests to this invitation.")
        serializer.save()

    @action(detail=False, methods=['post'])
    def bulk_create_guests(self, request):
        """
        Create multiple guests at once.
        Expects a list of guest objects in the body.
        """
        # If the data is a list, we treat it as bulk create
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of guests for bulk creation."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Validate all items
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        
        # Check ownership/permission for all items
        for item in serializer.validated_data:
            invitation = item.get('invitation')
            
            if not invitation:
                continue

            # Check Owner
            is_owner = invitation.user == request.user
            # Check Member Role
            is_editor = invitation.members.filter(
                user=request.user, 
                role__in=['owner', 'editor']
            ).exists()
            
            if not (is_owner or is_editor):
                return Response(
                    {"detail": "You do not have permission to add guests to one or more invitations."}, 
                    status=status.HTTP_403_FORBIDDEN
                )

        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['post'])
    def bulk_delete_guests(self, request):
        """
        Delete multiple guests at once.
        Expects a list of guest IDs in `guest_ids`.
        """
        guest_ids = request.data.get('guest_ids', [])
        if not guest_ids or not isinstance(guest_ids, list):
             return Response(
                {"detail": "Expected a list of 'guest_ids'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Filter guests to ensure they belong to user
        qs = self.get_queryset().filter(id__in=guest_ids)
        deleted_count, _ = qs.delete()
        
        return Response({"deleted": deleted_count}, status=status.HTTP_200_OK)
