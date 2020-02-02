# Core Django imports
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator

# Third-party app imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Imports from my apps
from ..bolo_logger import log_bolo


# Create your views here.
class AuthUserView(APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            """ LOGIN """
            login_credentials = request.data
            au = authenticate(request, **login_credentials)
            if au is not None:
                login(request, au)
                return Response({"message": "logged in successfuly"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """ LOG OUT """
        logout(request)
        return Response({"message": "logout successfully"}, status=status.HTTP_200_OK)