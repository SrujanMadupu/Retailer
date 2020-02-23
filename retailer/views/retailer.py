# Stdlib imports

# Core Django imports
from django.contrib.auth.models import User

# Third-party app imports
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView

# Imports from your apps
from .. models import Retailer
from .. serializers import RetailerSerializer
from .. bolo_logger import log_bolo


class RetailerViewSet(ModelViewSet):
    queryset = Retailer.objects.all()
    serializer_class = RetailerSerializer

    def create(self, request, *args, **kwargs):
        """ Create a Retailer """
        try:
            serializer = RetailerSerializer(data=request.data)
            if serializer.is_valid():
                obj_retailer = serializer.save()
                User.objects.create_user(username=obj_retailer.email, email=obj_retailer.email,
                                         password=obj_retailer.password)
                return Response({"message": "Retailer {} created successfully".
                                format(obj_retailer.name)}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
