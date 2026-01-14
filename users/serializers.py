from django.contrib.auth import get_user_model
from rest_framework import serializers
from invitations.serializers import InvitationDataSerializer
from guests.serializers import GuestSerializer
from payments.serializers import PaymentSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    userId = serializers.CharField(source='id')
    name = serializers.CharField(source='first_name') # Using first_name as name or get_full_name
    picture = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['userId', 'name', 'email', 'picture', 'projects']

    def get_picture(self, obj):
        if hasattr(obj, 'profile') and obj.profile.google_picture_url:
            return obj.profile.google_picture_url
        return ""

    def get_projects(self, obj):
        # Retrieve the invitation data related to the user
        # We assume 1 User has 1 InvitationData as their "Project"
        if hasattr(obj, 'invitation_data'):
            inv_data = obj.invitation_data
            
            # Fetch related data
            guests = inv_data.guests.all()
            payment = getattr(inv_data, 'payment', None)

            return {
                'invitationData': InvitationDataSerializer(inv_data).data,
                'management': GuestSerializer(guests, many=True).data,
                'payment': PaymentSerializer(payment).data if payment else None
            }
        
        # If no project exists yet, return None or an empty structure
        return None
