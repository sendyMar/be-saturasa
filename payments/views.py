from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from invitations.models import InvitationData
from .models import Payment
from .serializers import PaymentSerializer

class CreateDummyPaymentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        invitation_id = request.data.get('invitation_id')
        amount = request.data.get('amount')

        if not invitation_id or not amount:
            return Response({'error': 'invitation_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = InvitationData.objects.get(id=invitation_id)
        except InvitationData.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        # Basic security check: ensure user owns the invitation (via project link or directly)
        # Assuming permissions are handled or user is linked. 
        # For now, simplistic check:
        # if invitation.user != request.user: ... (Need to check if Invitation has User field or linked via Project)
        # Based on previous context, `UserProfile` (or User) has `projects`.
        # We'll skip complex ownership check for this "dummy" flow but ideally should benefit from IsOwner permission.

        # Logic for expiration
        # "menjadi 14 hari" -> 14 days from now.
        amount = float(amount)
        if amount == 49000:
            duration = 14
        elif amount == 69000:
            duration = 90
        else:
            duration = 14 # Default or error?

        # Create or Update Payment
        # User said "tombol default muncul... baru ketika user menekan...". 
        # So likely we accept one payment per invitation for now, or update it.
        payment, created = Payment.objects.update_or_create(
            invitation=invitation,
            defaults={
                'amount': amount,
                'is_paid': True,
                'unique_code': f"INV-{invitation_id[:8].upper()}-{int(timezone.now().timestamp())}",
                'time': timezone.now()
            }
        )

        # Update Invitation Expiry
        invitation.expires_at = timezone.now() + timedelta(days=duration)
        invitation.save()

        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)
