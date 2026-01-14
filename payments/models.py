from django.db import models
from invitations.models import InvitationData

class Payment(models.Model):
    invitation = models.OneToOneField(InvitationData, on_delete=models.CASCADE, related_name='payment')
    is_paid = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    unique_code = models.CharField(max_length=50) # e.g. "INV-123"
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.unique_code} - {self.amount}"
