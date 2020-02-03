# Stdlib imports
import requests

# Core Django imports
from django.db import transaction, DatabaseError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator

# Third-party app imports
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from ..throttles import ShipmentRateThrottle

# Imports from my apps
from ..credentials import api_url
from ..decorators import check_auth
from ..bolo_logger import log_bolo
from ..auth_token import get_bearer_token, read_bearer_token
from ..models import *
from ..serializers import ShipmentSerializer


class ShipmentViewSet(ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


class ShipmentAPIView(APIView):
    throttle_classes = [ShipmentRateThrottle]

    @staticmethod
    def get_shipment_detail(shipment_id, user):
        """requesting third party api for shipment_details using shipment id"""
        url = 'https://api.bol.com/retailer/shipments/'+str(shipment_id)
        headers = {'Accept': 'application/vnd.retailer.v3+json',
                   'Authorization': 'Bearer ' + str(read_bearer_token())}
        res = requests.get(url=url, headers=headers, verify=False)
        if res.status_code == 401:
            obj_retailer = Retailer.objects.get(email=user.email)
            get_bearer_token(obj_retailer.client_id, obj_retailer.client_secret)
            headers.update({'Authorization': 'Bearer ' + str(read_bearer_token())})
            res = requests.get(url=url, headers=headers, verify=False)
            return res.json()
        else:
            return res.json()

    @staticmethod
    def get_shipment(url, method, headers, user):
        """requesting third party api for shipments"""
        page = 1
        while page:
            new_url = url+"?page="+str(page)+"&fulfilment-method="+method
            print(">>> for page {}, url {}".format(page, new_url))
            res = requests.get(url=new_url, headers=headers, verify=False)
            res_json = res.json()
            if res.status_code == 401:
                obj_retailer = Retailer.objects.get(email=user.email)
                get_bearer_token(obj_retailer.client_id, obj_retailer.client_secret)
                headers.update({'Authorization': 'Bearer ' + str(read_bearer_token())})
                res = requests.get(url=new_url, headers=headers, verify=False)
                page = page + 1
                yield res.json()
            elif len(res_json) > 0:
                yield res_json
                page = page + 1
                continue
            else:
                raise StopIteration

    @staticmethod
    def save_shipments(data, user):
        """saving collected shipments data"""
        try:
            with transaction.atomic():
                for shipment in data['shipments']:
                    shipment_items = shipment.pop('shipmentItems')
                    transport = shipment.pop('transport')
                    customer_details = shipment.pop('customerDetails')
                    billing_details = shipment.pop('billingDetails')
                    obj_retailer = Retailer.objects.get(email=user.email)
                    obj_shipment = Shipment(**shipment)
                    obj_shipment.retailer = obj_retailer
                    obj_shipment.save()
                    for item in shipment_items:
                        obj_shipment.shipmentitems.create(**item)
                    obj_transport = Transport(**transport)
                    obj_transport.shipment = obj_shipment
                    obj_transport.save()
                    obj_cust = CustomerDetails(**customer_details)
                    obj_cust.shipment = obj_shipment
                    obj_cust.save()
                    obj_billing = BillingDetails(**billing_details)
                    obj_billing.shipment = obj_shipment
                    obj_billing.save()
        except (DatabaseError, KeyError, TypeError) as e:
            raise e

    @staticmethod
    def check_shipment_ids(shipment_ids):
        for id in shipment_ids:
            if Shipment.objects.filter(pk=id).exists():
                shipment_ids.remove(id)
        return shipment_ids

    @staticmethod
    def get_util(user):
        """
        utility method for collecting shipments
        using fulfillment methods 'FBR' and 'FBB' until receive empty response
        """
        ff_methods = ['FBR', 'FBB']
        url = api_url + '/retailer/shipments'
        headers = {'Accept': 'application/vnd.retailer.v3+json',
                   'Authorization': 'Bearer ' + str(read_bearer_token())}
        shipments = {'shipments': []}
        shipment_ids = []
        print(">>>>> initially shipments >>>", shipments)
        for method in ff_methods:
            shipment_gen = ShipmentAPIView.get_shipment(url, method, headers, user)
            for sh in shipment_gen:
                shipment_ids += [record['shipmentId'] for record in sh['shipments']]
                print(">>> for method {0} shipments {1}".format(method, shipment_ids))
            del shipment_gen
        for sh_id in shipment_ids:
            if not Shipment.objects.filter(shipmentId=sh_id).exists():
                shipments['shipments'].append(ShipmentAPIView.get_shipment_detail(sh_id, user))
            else:
                print(">>> shipment id {} already exists".format(sh_id))
        print(">>>> final response >>>", shipments)
        ShipmentAPIView.save_shipments(shipments, user)
        return shipments

    @method_decorator(login_required)
    @check_auth
    def get(self, request, *args, **kwargs):
        try:
            print(">>>> current user ", request.user)
            res = self.get_util(request.user)
            return Response({"message": res}, status=status.HTTP_200_OK)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
