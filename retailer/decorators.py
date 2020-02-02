from .auth_token import get_bearer_token
import os
from django.http import HttpResponse


def check_auth(f):
    def wrapper(cls, request, *args, **kwargs):
        if os.stat("retailer/access_token.txt").st_size == 0:
            if get_bearer_token():
                return f(cls, request, *args, **kwargs)
            else:
                return HttpResponse("Authentication Failed..Please try again")
        else:
            print(">>> token already exists")
            return f(cls, request, *args, **kwargs)
    return wrapper

