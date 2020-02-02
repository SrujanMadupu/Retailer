# Stdlib imports
from datetime import date, datetime

# Core Django imports
from django.contrib.auth.models import User

# Third-party app imports
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

import logging

# Imports from your apps
from .. models import Retailer
from .. forms import RetailerForm
from .. serializers import RetailerSerializer
from .. bolo_logger import log_bolo


class RetailerViewSet(ModelViewSet):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer
    # permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """ Create a Retailer """
        try:
            user_form = RetailerForm
            print(request.data)
            formset = user_form(request.data)
            if formset.is_valid():
                ouser = formset.save(commit=False)
                ouser.save()
                auth_user = User.objects.create_user(username=ouser.email, email=ouser.email, password=ouser.password)
                print(">>> User object >>", auth_user)
                return Response({"uid": ouser.name}, status=status.HTTP_200_OK)
            else:
                return Response(formset.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """ Get a TblUser details """
        try:
            ouser = Retailer.objects.get(id=kwargs['pk'])
            serializer = RetailerSerializer(ouser)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
