from django.db import migrations

def backfill_members(apps, schema_editor):
    InvitationData = apps.get_model('invitations', 'InvitationData')
    InvitationMember = apps.get_model('invitations', 'InvitationMember')
    
    members_to_create = []
    for invitation in InvitationData.objects.all():
        if not InvitationMember.objects.filter(invitation=invitation, user=invitation.user).exists():
            members_to_create.append(InvitationMember(
                invitation=invitation,
                user=invitation.user,
                role='owner'
            ))
            
    if members_to_create:
        InvitationMember.objects.bulk_create(members_to_create)

class Migration(migrations.Migration):

    dependencies = [
        ('invitations', '0006_invitationticket_invitationmember'),
    ]

    operations = [
        migrations.RunPython(backfill_members),
    ]
