import os
import secrets
import time
import jwt

# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH=settings.JWT_AUTH

from .models import OauthAccessToken, OauthRefreshToken


def token_generate(user):
    access_token_jwt = jwt.encode({'jti':secrets.token_urlsafe(60)}, JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM'])
    refresh_token_jwt = jwt.encode({'jti':secrets.token_urlsafe(60)}, JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM'])

    # Expiry for access token is 7 days
    expiry_at = round(time.time() + (7 * 24 * 60 * 60))

    user_details = {"token_type": "Bearer",
    "access_token": access_token_jwt,
    "expiry_at": expiry_at,
    "refresh_token": refresh_token_jwt,}
    OauthAccessToken.objects.update_or_create(owner=user,defaults={'access_token': str(access_token_jwt)[2:-1], 'expiry_at': expiry_at})

    #Expiry for refresh token is 30 days
    OauthRefreshToken.objects.update_or_create(owner=user,defaults={'refresh_token': str(refresh_token_jwt)[2:-1], 
    'expiry_at': round(time.time() + (30 * 24 * 60 * 60))})
    return user_details