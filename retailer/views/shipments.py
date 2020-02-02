# Stdlib imports
import requests

# Core Django imports
from django.db import transaction, DatabaseError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator

# Third-party app imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Imports from my apps
from ..credentials import api_url
from ..decorators import check_auth
from ..bolo_logger import log_bolo
from ..auth_token import get_bearer_token
from ..models import Shipment, Retailer


class ShipmentsView(APIView):

    # @staticmethod
    # def shipments(url, method, headers):
    #     res = requests.get(url=url, headers=headers, verify=False)
    #     print(">>>> shipments response >>>", res.json())
    #     return res.json()

    @staticmethod
    def get_shipment(url, method, headers):
        # https: // api.bol.com / retailer / shipments?page = 1 & fulfilment - method = FBR
        page = 1
        while page:
            new_url = url+"?page="+str(page)+"&fulfilment-method="+method
            # print(">>> for page {}, url {}".format(page, new_url))
            res = requests.get(url=new_url, headers=headers, verify=False)
            res_json = res.json()
            if len(res_json) > 0:
                if 'shipments' in res_json:
                    yield res_json
                elif res_json['title'] == 'Expired JWT' and res_json['status'] == 401:
                    get_bearer_token()
                    headers.update({'Authorization': 'Bearer ' + ShipmentsView.read_access_key()})
                    res = requests.get(url=new_url, headers=headers, verify=False)
                    yield res.json()
                page = page + 1
                continue
            else:
                raise StopIteration

    @staticmethod
    def read_access_key():
        with open('retailer/access_token.txt', 'r') as tk:
            token = tk.read()
        return token

    @staticmethod
    def save_shipments(data, user):
        try:
            with transaction.atomic():
                for shipment in data['shipments']:
                    """ get shipment details """
                    shipment_items = shipment.pop('shipmentItems')
                    shipment['transportId'] = shipment.pop('transport')['transportId']
                    shipment['retailer'] = Retailer.objects.get(email=user.email)
                    obj_shipment = Shipment.objects.create(**shipment)
                    # for item in shipment_items:
                    #     obj_shipment.shipmentitems.create(**item)
        except (DatabaseError, KeyError, TypeError) as e:
            raise e

    @method_decorator(login_required)
    @check_auth
    def get(self, request, *args, **kwargs):
        try:
            print(">>>> current user ", request.user)
            ff_methods = ['FBR', 'FBB']
            url = api_url + '/retailer/shipments'
            headers = {'Accept': 'application/vnd.retailer.v3+json',
                       'Authorization': 'Bearer ' + self.read_access_key()}
            shipments = {'shipments': []}
            print(">>>>> initially shipments >>>", shipments)
            for method in ff_methods:
                shipment_gen = self.get_shipment(url, method, headers)
                for sh in shipment_gen:
                    shipments['shipments'] += sh['shipments']
                    print(">>> for method {0} shipments {1}".format(method, shipments))
                del shipment_gen
            # res_json = self.get_shipments()
            # if 'shipments' in res_json:
            #     self.save_shipments(res_json, request.user)
            #     return Response(res_json, status=status.HTTP_200_OK)
            # elif res_json['title'] == 'Expired JWT' and res_json['status'] == 401:
            #     """ access_token has been expired , so request for new access token """
            #     print(">>> Requesting For New Access Token <<<<")
            #     if get_bearer_token():
            #         res_json = self.get_shipments()
            #         self.save_shipments(res_json, request.user)
            #         return Response(res_json, status=status.HTTP_200_OK)
            #     else:
            #         return Response({'message': "Authentication Failed..try again later!"}, status=status.HTTP_200_OK)
            # else:
            #     return Response(res_json, status=status.HTTP_200_OK)
            self.save_shipments(shipments, request.user)
            return Response(shipments, status=status.HTTP_200_OK)
        except Exception as e:
            log_bolo.error(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
