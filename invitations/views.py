from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from datetime import timedelta
import secrets
import hashlib
from .models import InvitationData, InvitationMember, InvitationTicket
from .serializers import (
    InvitationDataSerializer, 
    InvitationTicketSerializer, 
    JoinInvitationSerializer
)

class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationDataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # LAZY DELETION: Cek expired setiap kali user mengakses list/invitation
        from django.utils import timezone
        now = timezone.now()
        
        # Hapus undangan yang sudah lewat masa aktif
        InvitationData.objects.filter(user=self.request.user, expires_at__lt=now).delete()
        
        # Users can only see their own invitations OR where they are members
        return InvitationData.objects.filter(
            Q(user=self.request.user) | Q(members__user=self.request.user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        # Auto-assign user
        invitation = serializer.save(user=self.request.user)
        
        # Juga tambahkan sebagai Member Owner agar konsisten
        InvitationMember.objects.create(
            invitation=invitation,
            user=self.request.user,
            role='owner'
        )

    @action(detail=True, methods=['post'], url_path='invite')
    def invite_user(self, request, pk=None):
        invitation = self.get_object()
        
        # Validasi Permission: Hanya Owner atau Editor yang bisa invite
        # Cek apakah req.user adalah owner
        is_owner = invitation.user == request.user
        # Cek apakah req.user adalah member dengan role owner/editor
        is_editor = invitation.members.filter(
            user=request.user, 
            role__in=['owner', 'editor']
        ).exists()
        
        if not (is_owner or is_editor):
            return Response(
                {'error': 'You do not have permission to invite users.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = request.data.get('email')
        role = request.data.get('role', 'viewer')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Generate Secure Token
        token = secrets.token_urlsafe(16) # e.g. "DUE83_..."
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # 2. Set Expiry (1 Day)
        # Import timezone locally if strictly needed or use from django.utils
        from django.utils import timezone
        expires_at = timezone.now() + timedelta(days=1)
        
        # 3. Create Ticket
        ticket = InvitationTicket.objects.create(
            invitation=invitation,
            email=email,
            token=token, # Save plain token for Owner Dashboard
            token_hash=token_hash,
            role=role,
            expires_at=expires_at
        )
        
        # 4. Return Token (Plain) to User to share
        return Response({
            'token': token,
            'email': email,
            'role': role,
            'expires_at': expires_at,
            'note': 'Share this token manually to the user.'
        })

    @action(detail=False, methods=['post'], url_path='join')
    def join_invitation(self, request):
        serializer = JoinInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        from django.utils import timezone
        
        # 1. Cari Ticket
        try:
            ticket = InvitationTicket.objects.get(
                token_hash=token_hash,
                is_claimed=False,
                expires_at__gt=timezone.now()
            )
        except InvitationTicket.DoesNotExist:
             return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
             
        # 2. Identity Binding Check
        if ticket.email != request.user.email:
             return Response(
                 {'error': f'This token belongs to {ticket.email}, but you are {request.user.email}'}, 
                 status=status.HTTP_403_FORBIDDEN
             )
             
        # 3. Assign Member
        InvitationMember.objects.get_or_create(
            invitation=ticket.invitation,
            user=request.user,
            defaults={'role': ticket.role}
        )
        
        # 4. Burn Ticket
        ticket.is_claimed = True
        ticket.save()
        
        return Response({
            'status': 'joined', 
            'invitation_id': ticket.invitation.id,
            'slug': ticket.invitation.slug
        })

    @action(detail=False, methods=['get'], url_path='my-pending')
    def my_pending_tickets(self, request):
        """
        List active (unclaimed, not expired) tickets for the current user's email.
        This allows the frontend to show a "You have an invitation!" notification/list.
        """
        from django.utils import timezone
        tickets = InvitationTicket.objects.filter(
            email=request.user.email,
            is_claimed=False,
            expires_at__gt=timezone.now()
        )
        # Reuse serializer but maybe include invitation details?
        # Actually InvitationTicketSerializer is basic. Let's send basic info.
        # Ideally we want to show "Invitation from [Owner] for [Groom] & [Bride]"
        # We can create a simple custom response or enhance serializer.
        # For simplicity, returning serialized tickets. Frontend can use ID to join? 
        # Wait, ticket serializer has 'token' but that's plaintext for owner only. 
        # For invitee, we just need to know it exists. 
        # BUT wait, how do they join? They need the TOKEN string. 
        # If we return the token here, it bypasses the "manual share" security model...
        # UT check: "Identity Binding" -> Token only works for email owner.
        # If I am the email owner (authenticated), is it safe to show me the token?
        # YES. If I am logged in as bob@example.com, and the ticket is for bob@example.com,
        # it is perfectly safe to give me the token to click "Join".
        # So I will expose the token in this specific endpoint.
        
        data = []
        for t in tickets:
            data.append({
                'id': t.id,
                'email': t.email,
                'role': t.role,
                # 'token': t.token, # REMOVED: User must input manually for security
                'expires_at': t.created_at, 
                'invitation_groom': t.invitation.groom_name,
                'invitation_bridal': t.invitation.bridal_name,
                'invitation_owner': t.invitation.user.username
            })
            
        return Response(data)
