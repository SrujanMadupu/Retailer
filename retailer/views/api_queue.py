from django.utils.decorators import method_decorator
from ..decorators import check_auth
from ..bolo_logger import log_bolo
from django.contrib.auth.decorators import login_required
import django_rq as rq
from rest_framework.response import Response
from rest_framework import status
from .shipments import *
from rest_framework.views import APIView
from ..throttles import ShipmentRateThrottle
from time import sleep


def greeting(name):
    return f"welcome {name}"


class ShipmentAPIView(APIView):
    throttle_classes = [ShipmentRateThrottle]

    @method_decorator(login_required)
    @check_auth
    def get(self, request, *args, **kwargs):
        try:
            print(">>>> current user ", request.user)
            user_email = request.user.email
            job1 = rq.enqueue(get_util, user_email)
            while not job1.is_finished:
                sleep(1)
            print(">>>> job1 result >>>", job1.result)
            job2 = rq.enqueue(shipment_details_util, job1.result, user_email)
            while not job2.is_finished:
                sleep(1)
            print(">>>> job2 result >>>", job2.result)
            job3 = rq.enqueue(save_shipments_util, job2.result, user_email)
            return Response({"message": "successfully fetched data and saved in db"}, status=status.HTTP_200_OK)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)