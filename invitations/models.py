import uuid
from django.db import models
from django.conf import settings
from core.models import Template, Song # <--- Import dari app core

class InvitationData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invitations')
    
    # Relationships (Optional biar bisa null pas awal create)
    theme = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations')
    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True, blank=True, related_name='invitations')
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    slug = models.SlugField(unique=True, db_index=True, max_length=200, blank=True)

    # Data Mempelai
    groom_name = models.CharField(max_length=200)
    bridal_name = models.CharField(max_length=200)
    dad_groom_name = models.CharField(max_length=200)
    mom_groom_name = models.CharField(max_length=200)
    dad_bridal_name = models.CharField(max_length=200)
    mom_bridal_name = models.CharField(max_length=200)

    # Texts
    sentence_opening = models.TextField(blank=True, default='')
    sentence_greeting = models.TextField(blank=True, default='')
    sentence_middlehook = models.TextField(blank=True, default='') # HTML/Markdown content
    sentence_closing = models.TextField(blank=True, default='')

    # Images (Simpan URL/Path)
    img_cover = models.CharField(max_length=500, blank=True, default='')
    img_groom = models.CharField(max_length=500, blank=True, default='')
    img_bridal = models.CharField(max_length=500, blank=True, default='')
    
    # JSON Fields (Untuk Array String)
    img_gallery = models.JSONField(default=list, blank=True) 

    def save(self, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta
        # Set Default Expiration: 3 Days
        if not self.id or not self.expires_at:
             self.expires_at = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.groom_name} & {self.bridal_name}"

class BankAccount(models.Model):
    invitation = models.ForeignKey(InvitationData, on_delete=models.CASCADE, related_name='digital_gifts')
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    account_holder = models.CharField(max_length=200)

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invitation = models.ForeignKey(InvitationData, on_delete=models.CASCADE, related_name='events')
    event_name = models.CharField(max_length=200)
    address = models.TextField()
    gmaps_link = models.URLField(max_length=500)
    date = models.DateField()
    time = models.CharField(max_length=50)     # Start Time
    time_end = models.CharField(max_length=50) # End Time