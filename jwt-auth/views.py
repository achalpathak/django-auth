import os
import random
import secrets
import time
import jwt
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password, check_password

# To import user model from project "settings.py" file
from django.contrib.auth import get_user_model
Users = get_user_model()


from .models import OauthAccessToken, OauthRefreshToken

# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH=settings.JWT_AUTH

# To generate user_details={'token_type','access_token','expiry_at','refresh_token'}
from .token_generate import token_generate

# Decorator to check if Authorization header is present and is valid
from .decorators import check_authorization

# @api_view(['POST'])
# @check_authorization
# @permission_classes([AllowAny, ])
# def sensitive(request):
#     """
#     Input should be in the format:
#     {"email": "admin@gmail.com", "password": "admin"}
#     """
#     res = {'error': 'This is a sensitive endpoint.'}
#     return Response(res, status=status.HTTP_200_OK)


# To issue new token after authenticating the user
@api_view(['POST'])
@permission_classes([AllowAny, ])
def token(request):
    """
    Input should be in the format:
    {"email": "admin@gmail.com", "password": "admin"}
    """
    try:
        email = request.data['email']
        password = request.data['password']
        try:
            user = Users.objects.get(email=email)
            if not check_password(request.data['password'], user.password):
                user = None
        except Users.DoesNotExist:
            user = None

        if user is not None:
            try:
                user_details=token_generate(user)
                return Response(user_details, status=status.HTTP_200_OK) 
            except Exception as e:
                raise e
        else:
            res = {
                'error': 'Can not authenticate with the given credentials or the account has been deactivated.'}
            return Response(res, status=status.HTTP_403_FORBIDDEN)
    except KeyError:
        res = {'error': 'Please provide a email and a password.'}
        return Response(res)


# To issue new token from refresh token
@api_view(['POST'])
@permission_classes([AllowAny, ])
def refresh_token(request):
    """
    Input should be in the format:
    {"refresh_token": "<token>"}
    """
    try:
        refresh_token = request.data['refresh_token']
        jwt.decode(refresh_token, JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM'])
        refresh_token_db = OauthRefreshToken.objects.filter(refresh_token__exact=refresh_token).values()
        for i in refresh_token_db:
            user_db=i['owner_id']
        user_details=token_generate(user_db)
        return Response(user_details, status=status.HTTP_200_OK)    
    except (KeyError,jwt.DecodeError):
        res = {'error': 'Please provide a valid refresh token.'}
        return Response(res)