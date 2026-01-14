from rest_framework import serializers
from .models import Guest
from django.utils.text import slugify
import uuid

class GuestSerializer(serializers.ModelSerializer):
    isSent = serializers.BooleanField(source='is_sent', default=False)
    viewAt = serializers.DateTimeField(source='view_at', allow_null=True, required=False)
    isClickedATM = serializers.BooleanField(source='is_clicked_atm', default=False)
    paxRequest = serializers.IntegerField(source='pax_request', allow_null=True, required=False)
    paxConfirmed = serializers.IntegerField(source='pax_confirmed', allow_null=True, required=False)

    class Meta:
        model = Guest
        fields = [
            'id', 'name', 'slug', 'type', 'wa', 'email',
            'isSent', 'viewAt', 'isClickedATM', 'rsvp',
            'paxRequest', 'paxConfirmed', 'greetings',
            'invitation'  # Added invitation
        ]
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True},
            'invitation': {'required': True}
        }

    def create(self, validated_data):
        # Auto-generate slug if missing
        if 'slug' not in validated_data or not validated_data['slug']:
            base_slug = slugify(validated_data.get('name', 'guest'))
            # Ensure unique slug by appending simplified UUID
            validated_data['slug'] = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        
        return super().create(validated_data)
