from rest_framework import serializers
from django.contrib.auth.models import User
from .models import InvitationData, Event, BankAccount, InvitationMember, InvitationTicket
from core.models import Template, Song
from payments.serializers import PaymentSerializer

class UserRefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InvitationMemberSerializer(serializers.ModelSerializer):
    user = UserRefSerializer(read_only=True)
    joinedAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = InvitationMember
        fields = ['id', 'user', 'role', 'joinedAt']

class InvitationTicketSerializer(serializers.ModelSerializer):
    expiresAt = serializers.DateTimeField(source='expires_at', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    isClaimed = serializers.BooleanField(source='is_claimed', read_only=True)

    class Meta:
        model = InvitationTicket
        fields = ['id', 'email', 'role', 'token', 'expiresAt', 'isClaimed', 'createdAt']

class JoinInvitationSerializer(serializers.Serializer):
    token = serializers.CharField()

class BankAccountSerializer(serializers.ModelSerializer):
    bankName = serializers.CharField(source='bank_name')
    accountNumber = serializers.CharField(source='account_number')
    accountHolder = serializers.CharField(source='account_holder')

    class Meta:
        model = BankAccount
        fields = ['bankName', 'accountNumber', 'accountHolder']

class EventSerializer(serializers.ModelSerializer):
    eventName = serializers.CharField(source='event_name')
    gmapsLink = serializers.CharField(source='gmaps_link')
    timeEnd = serializers.CharField(source='time_end')

    class Meta:
        model = Event
        fields = ['id', 'eventName', 'address', 'gmapsLink', 'date', 'time', 'timeEnd']

class InvitationDataSerializer(serializers.ModelSerializer):
    idTheme = serializers.PrimaryKeyRelatedField(source='theme', queryset=Template.objects.all(), required=False, allow_null=True)
    themeName = serializers.CharField(source='theme.name', read_only=True)
    idSong = serializers.PrimaryKeyRelatedField(source='song', queryset=Song.objects.all(), required=False, allow_null=True)
    
    # We use source='created_at' but name it createdAt for TS
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    expiresAt = serializers.DateTimeField(source='expires_at', read_only=True)

    # Data Mempelai
    groomName = serializers.CharField(source='groom_name')
    bridalName = serializers.CharField(source='bridal_name')
    dadGroomName = serializers.CharField(source='dad_groom_name')
    momGroomName = serializers.CharField(source='mom_groom_name')
    dadBridalName = serializers.CharField(source='dad_bridal_name')
    momBridalName = serializers.CharField(source='mom_bridal_name')
    
    # Lists
    eventList = EventSerializer(source='events', many=True, required=False)
    digitalGifts = BankAccountSerializer(source='digital_gifts', many=True, required=False)
    payment = PaymentSerializer(read_only=True)
    
    # RBAC
    members = InvitationMemberSerializer(many=True, read_only=True)
    tickets = serializers.SerializerMethodField()
    myRole = serializers.SerializerMethodField()

    def get_tickets(self, obj):
        # Only show tickets to Owner or Editor
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return []
            
        # Check permissions
        can_see_tickets = False
        if obj.user == request.user:
            can_see_tickets = True
        elif hasattr(obj, 'members'):
            member = next((m for m in obj.members.all() if m.user == request.user), None)
            if member and member.role in ['owner', 'editor']:
                can_see_tickets = True
        
        if can_see_tickets and hasattr(obj, 'tickets'):
            # Return active (unclaimed, not expired) tickets
            # Note: We might want all tickets even if expired? 
            # User said "calon members ... members yang sedang di invite".
            # Usually implies active.
            from django.utils import timezone
            valid_tickets = obj.tickets.filter(is_claimed=False, expires_at__gt=timezone.now())
            return InvitationTicketSerializer(valid_tickets, many=True).data
            
        return []

    def get_myRole(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        # 1. Check if Owner
        if obj.user == request.user:
            return 'owner'
        
        # 2. Check if Member (Optimized with prefetch usually, but checks local cache first)
        # We can iterate over members.all() if it's prefetched
        if hasattr(obj, 'members'):
            member = next((m for m in obj.members.all() if m.user == request.user), None)
            if member:
                return member.role
                
        return None

    # Texts
    sentenceOpening = serializers.CharField(source='sentence_opening', required=False, allow_blank=True)
    sentenceGreeting = serializers.CharField(source='sentence_greeting', required=False, allow_blank=True)
    sentenceMiddlehook = serializers.CharField(source='sentence_middlehook', required=False, allow_blank=True)
    sentenceClosing = serializers.CharField(source='sentence_closing', required=False, allow_blank=True)

    # Images
    imgCover = serializers.CharField(source='img_cover', required=False, allow_blank=True)
    imgGroom = serializers.CharField(source='img_groom', required=False, allow_blank=True)
    imgBridal = serializers.CharField(source='img_bridal', required=False, allow_blank=True)
    imgGallery = serializers.JSONField(source='img_gallery', required=False)

    def _generate_unique_slug(self, name):
        import uuid
        from django.utils.text import slugify
        base_slug = slugify(name)
        if not base_slug:
            base_slug = 'invitation'
        
        slug = base_slug
        # Simple unique check loop
        while InvitationData.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        return slug

    def create(self, validated_data):
        events_data = validated_data.pop('events', [])
        gifts_data = validated_data.pop('digital_gifts', [])
        
        # Auto-generate Slug if missing or empty
        if not validated_data.get('slug'):
            groom = validated_data.get('groom_name', 'groom')
            bridal = validated_data.get('bridal_name', 'bridal')
            validated_data['slug'] = self._generate_unique_slug(f"{groom}-{bridal}")
        
        # Create Invitation (User will be passed from perform_create in View)
        invitation = InvitationData.objects.create(**validated_data)
        
        # Create Nested Events
        for event in events_data:
            Event.objects.create(invitation=invitation, **event)
            
        # Create Nested Gifts
        for gift in gifts_data:
            BankAccount.objects.create(invitation=invitation, **gift)
            
        return invitation

    def update(self, instance, validated_data):
        events_data = validated_data.pop('events', [])
        gifts_data = validated_data.pop('digital_gifts', [])
        
        # Update Slug if cleared? Or preserve? Usually preserve unless explicitly changed.
        # If slug is in validated_data and empty, generate new one?
        if 'slug' in validated_data and not validated_data['slug']:
            groom = validated_data.get('groom_name', instance.groom_name)
            bridal = validated_data.get('bridal_name', instance.bridal_name)
            validated_data['slug'] = self._generate_unique_slug(f"{groom}-{bridal}")

        # Update Main Fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update Events (Delete all and recreate)
        instance.events.all().delete()
        for event in events_data:
            Event.objects.create(invitation=instance, **event)
            
        # Update Gifts
        instance.digital_gifts.all().delete()
        for gift in gifts_data:
            BankAccount.objects.create(invitation=instance, **gift)
            
        return instance

    class Meta:
        model = InvitationData
        fields = [
            'id', 'idTheme', 'idSong', 'createdAt', 'expiresAt', 'slug',
            'groomName', 'bridalName', 'dadGroomName', 'momGroomName', 'dadBridalName', 'momBridalName',
            'id', 'idTheme', 'idSong', 'createdAt', 'expiresAt', 'slug',
            'groomName', 'bridalName', 'dadGroomName', 'momGroomName', 'dadBridalName', 'momBridalName',
            'eventList', 'digitalGifts', 'payment', 'members', 'tickets', 'myRole',
            'sentenceOpening', 'sentenceGreeting', 'sentenceMiddlehook', 'sentenceClosing',
            'imgCover', 'imgGroom', 'imgBridal', 'imgGallery',
            'theme', 'song', 'themeName' 
        ]
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True} 
        }
