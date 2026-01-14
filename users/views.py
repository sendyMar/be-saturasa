from rest_framework import views, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings

class GoogleLoginView(views.APIView):
    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the token
            # Note: You should replace 'YOUR_GOOGLE_CLIENT_ID' with settings.GOOGLE_CLIENT_ID if you store it there,
            # or pass the audience as one of the checks.
            # ideally getting client_id from env or settings.
            # For this MVP we will try to verify without strict audience check or assuming generic valid token for the email.
            
            # Use a proper client ID in production!
            id_info = id_token.verify_oauth2_token(token, google_requests.Request(), audience=settings.GOOGLE_CLIENT_ID, clock_skew_in_seconds=10)
            
            if 'accounts.google.com' not in id_info['iss']:
                 return Response({'error': 'Invalid issuer'}, status=status.HTTP_400_BAD_REQUEST)

            email = id_info['email']
            first_name = id_info.get('given_name', '')
            last_name = id_info.get('family_name', '')

            user, created = User.objects.get_or_create(username=email, defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })
            
            if created:
                user.set_unusable_password()
                user.save()
            
            # Update user info if changed
            if not created:
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()

            # Handle Profile Picture
            from .models import Profile
            picture_url = id_info.get('picture')
            profile, _ = Profile.objects.get_or_create(user=user)
            
            if picture_url and profile.google_picture_url != picture_url:
                profile.google_picture_url = picture_url
                profile.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'picture': profile.google_picture_url
                }
            })

        except ValueError as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
