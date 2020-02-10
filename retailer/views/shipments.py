# Stdlib imports
import requests
from time import time, sleep

# Core Django imports
from django.db import transaction, DatabaseError

# Third-party app imports
from rest_framework.viewsets import ModelViewSet

# Imports from my apps
from ..credentials import api_url
from ..auth_token import get_bearer_token, read_bearer_token
from ..models import *
from ..serializers import ShipmentSerializer

max_call_rate = 60


class ShipmentViewSet(ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer


def get_shipment_detail(shipment_id, user_email):
    """requesting third party api for shipment_details using shipment id"""
    url = 'https://api.bol.com/retailer/shipments/'+str(shipment_id)
    headers = {'Accept': 'application/vnd.retailer.v3+json',
               'Authorization': 'Bearer ' + str(read_bearer_token())}
    res = requests.get(url=url, headers=headers, verify=False)
    if res.status_code == 401:
        obj_retailer = Retailer.objects.get(email=user_email)
        get_bearer_token(obj_retailer.client_id, obj_retailer.client_secret)
        headers.update({'Authorization': 'Bearer ' + str(read_bearer_token())})
        res = requests.get(url=url, headers=headers, verify=False)
        return res.json()
    elif res.status_code == 429:
        return {}
    else:
        return res.json()


def get_shipment(url, method, headers, user_email):
    """requesting third party api for shipments"""
    page = 1
    start_time = time()
    while page:
        new_url = url+"?page="+str(page)+"&fulfilment-method="+method
        print(">>> for page {}, url {}".format(page, new_url))
        res = requests.get(url=new_url, headers=headers, verify=False)
        res_json = res.json()
        print(res_json)
        if res.status_code == 401:
            obj_retailer = Retailer.objects.get(email=user_email)
            get_bearer_token(obj_retailer.client_id, obj_retailer.client_secret)
            headers.update({'Authorization': 'Bearer ' + str(read_bearer_token())})
            res = requests.get(url=new_url, headers=headers, verify=False)
            page = page + 1
            yield res.json()
        elif res.status_code == 429:
            end_time = time()
            sleep_time = max_call_rate-(end_time - start_time)
            print("sleeping for >>> ", sleep_time)
            sleep(sleep_time)
            start_time = time()
            continue
        elif res.status_code == 200 and len(res_json) > 0:
            yield res_json
            page = page + 1
            continue
        elif res.status_code == 200 and len(res_json) == 0:
            break
    print(">>> got {} set, raising stopIteration")
    raise StopIteration


def save_shipments(data, user_email):
    """saving collected shipments data"""
    try:
        with transaction.atomic():
            for shipment in data['shipments']:
                shipment_items = shipment.pop('shipmentItems')
                transport = shipment.pop('transport')
                customer_details = shipment.pop('customerDetails')
                billing_details = shipment.pop('billingDetails')
                obj_retailer = Retailer.objects.get(email=user_email)
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


def get_util(user_email):
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
        shipment_gen = get_shipment(url, method, headers, user_email)
        for sh in shipment_gen:
            shipment_ids += [record['shipmentId'] for record in sh['shipments']]
            print(">>> for method {0} shipments {1}".format(method, shipment_ids))
        del shipment_gen
    return shipment_ids


def shipment_details_util(shipment_ids, user_email):
    shipments = {'shipments': []}
    start_time = time()
    while len(shipment_ids) > 0:
        sh_id = shipment_ids[0]
        sh_details = get_shipment_detail(sh_id, user_email)
        if len(sh_details) == 0:
            end_time = time()
            sleep_time = max_call_rate-(end_time-start_time)
            print(">>>sleeping for >>", sleep_time)
            sleep(sleep_time)
            start_time = time()
        else:
            shipments['shipments'].append(sh_details)
            shipment_ids.pop(0)
    print(">>>> final response >>>", shipments)
    return shipments


def save_shipments_util(shipments, user_email):
    save_shipments(shipments, user_email)
    return {"message": "Successfully saved shipments"}
