import time
import jwt

from rest_framework import status
from rest_framework.response import Response

from .models import OauthAccessToken, OauthRefreshToken

# To import JWT settings from project "settings.py" file
from django.conf import settings
JWT_AUTH=settings.JWT_AUTH

# Decorator to check if Authorization header is present and is valid
def check_authorization(function):
    def wrap(request, *args, **kwargs):
        try:
            # Check if Authorization header is present
            if request.META['HTTP_AUTHORIZATION']:
                if request.META['HTTP_AUTHORIZATION'][0:7].lower() != "bearer ":
                    raise Exception('Authorization Header is missing Bearer.')
                else:
                    # Check if the token is verified
                    try:
                        jwt.decode(request.META['HTTP_AUTHORIZATION'][7:], JWT_AUTH['JWT_SECRET'], algorithm=JWT_AUTH['JWT_ALGORITHM'])
                        # Check if the token is expired
                        db_data=OauthAccessToken.objects.filter(access_token__exact=request.META['HTTP_AUTHORIZATION'][7:]).values()
                        for i in db_data:
                            db_expiry_at=i['expiry_at']
                        if round(time.time()) < int(db_expiry_at):
                            return function(request, *args, **kwargs)
                        else:
                            raise Exception('Token has expired.')
                    except:
                        res = {'error':'Access token has expired, been revoked, or is otherwise invalid.'}
            else:
                raise Exception('Authorization Header is empty.')
        except:
            res = { 'error': 'Server could not verify authorization header.'}

        return Response(res, status=status.HTTP_403_FORBIDDEN)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
