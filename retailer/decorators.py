from .auth_token import get_bearer_token
import os
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from .models import Retailer


def check_auth(f):
    def wrapper(cls, request, *args, **kwargs):
        if os.stat("retailer/access_token.txt").st_size == 0:
            obj_retailer = Retailer.objects.get(email=request.user.email)
            if get_bearer_token(obj_retailer.client_id, obj_retailer.client_secret):
                return f(cls, request, *args, **kwargs)
            else:
                return HttpResponse("Authentication Failed..Please try again")
        else:
            print(">>> token already exists")
            return f(cls, request, *args, **kwargs)
    return wrapper


def check_post_keys(*req_args, **req_keys):
    def outer_wrapper(f):
        def inner_wrapper(cls, request, *args, **kwargs):
            print(">>> big wrapper keys >> ", req_keys)
            print(">>> request data keys >>>> ", request.data.keys())
            for key in req_keys['required_keys']:
                if key not in request.data.keys() or request.data[key] == "":
                    return Response({'KeyError': key+" is required"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return f(cls, request, *args, **kwargs)
        return inner_wrapper
    return outer_wrapper

