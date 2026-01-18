from rest_framework import serializers
from .models import Guest
from django.utils.text import slugify
import uuid

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = [
            'id', 'name', 'slug', 'type', 'wa', 'email',
            'is_sent', 'view_at', 'is_clicked_atm', 'rsvp',
            'pax_request', 'pax_confirmed', 'greetings',
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
