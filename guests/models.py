import uuid
from django.db import models
from invitations.models import InvitationData

class Guest(models.Model):
    TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invitation = models.ForeignKey(InvitationData, on_delete=models.CASCADE, related_name='guests')
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    wa = models.CharField(max_length=50) # Whatsapp number
    email = models.EmailField(null=True, blank=True)
    
    is_sent = models.BooleanField(default=False)
    view_at = models.DateTimeField(null=True, blank=True)
    is_clicked_atm = models.BooleanField(default=False)
    
    rsvp = models.CharField(max_length=50, null=True, blank=True) 
    # rsvp could be a choice field (Pending, Yes, No) but using Char for flexibility as per TS string

    pax_request = models.PositiveIntegerField(null=True, blank=True)
    pax_confirmed = models.PositiveIntegerField(null=True, blank=True)
    
    greetings = models.JSONField(default=list) # string[]

    def __str__(self):
        return f"{self.name} ({self.type})"
