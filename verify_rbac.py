import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from invitations.models import InvitationData, InvitationMember, InvitationTicket
from rest_framework.test import APIRequestFactory, force_authenticate
from invitations.views import InvitationViewSet

# Setup Users
user_a, _ = User.objects.get_or_create(username='usera_rbac', email='usera_rbac@example.com')
user_b, _ = User.objects.get_or_create(username='userb_rbac', email='userb_rbac@example.com')

# Setup ViewSet
factory = APIRequestFactory()
view_invite = InvitationViewSet.as_view({'post': 'invite_user'})
view_join = InvitationViewSet.as_view({'post': 'join_invitation'})

# Cleanup old test data
InvitationData.objects.filter(slug='test-rbac-slug').delete()

# 1. Create Invitation for User A
invitation = InvitationData.objects.create(
    user=user_a, 
    groom_name='Groom', 
    bridal_name='Bride',
    slug='test-rbac-slug'
)
# Ensure Owner Member created (simulating viewset perform_create)
InvitationMember.objects.get_or_create(invitation=invitation, user=user_a, role='owner')

print(f"Created Invitation: {invitation.slug} by {user_a}")

# 2. Invite User B (as User A)
request = factory.post(f'/invitations/{invitation.id}/invite/', {'email': 'userb_rbac@example.com', 'role': 'editor'}, format='json')
force_authenticate(request, user=user_a)
response = view_invite(request, pk=invitation.id)
print(f"Invite Response Status: {response.status_code}")
if response.status_code != 200:
    print(response.data)
    exit(1)

token = response.data['token']
print(f"Got Token: {token}")

# 3. Join as User B
request_join = factory.post('/invitations/join/', {'token': token}, format='json')
force_authenticate(request_join, user=user_b)
response_join = view_join(request_join)
print(f"Join Response Status: {response_join.status_code}")

if response_join.status_code == 200:
    print("Join Success!")
else:
    print(response_join.data)

# 4. Verify Membership
is_member = InvitationMember.objects.filter(invitation=invitation, user=user_b, role='editor').exists()
print(f"User B includes Editor role: {is_member}")

# 5. Verify Ticket Burned
ticket = InvitationTicket.objects.filter(invitation=invitation, email='userb_rbac@example.com').last()
print(f"Ticket Claimed: {ticket.is_claimed}")
