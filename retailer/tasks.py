# Create your tasks here
from __future__ import absolute_import, unicode_literals
import json
from celery import shared_task, task
from celery.result import AsyncResult
from celery.signals import task_success, after_task_publish
from retailer.models import Retailer
from .decorators import read_bearer_token, get_bearer_token
from .credentials import api_url
import requests
from time import time, sleep
from .models import Shipment
from django.db import transaction, DatabaseError
from .serializers import *
from bolo.celery import app
from .bolo_logger import log_bolo

MAX_CALL_RATE = 60


class RateLimitException(Exception):
    def __init__(self, r):
        self.retry_after = r


def get_shipment_util(url, method, headers, user_email):
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
            sleep_time = MAX_CALL_RATE-(end_time - start_time)
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


@task
def get_shipment(user_email):
    """
    utility method for collecting shipments
    using fulfillment methods 'FBR' and 'FBB' until receive empty response
    """
    obj_retailer = Retailer.objects.get(email=user_email)
    ff_methods = ['FBR', 'FBB']
    url = api_url + '/retailer/shipments'
    headers = {'Accept': 'application/vnd.retailer.v3+json',
               'Authorization': 'Bearer ' + str(read_bearer_token())}
    shipment_ids = []
    for method in ff_methods:
        shipment_gen = get_shipment_util(url, method, headers, user_email)
        for sh in shipment_gen:
            for record in sh['shipments']:
                Shipment.objects.create(shipmentId=record['shipmentId'],
                                        shipmentDate=record['shipmentDate'],
                                        retailer_id=obj_retailer.id)
                shipment_ids += [record['shipmentId']]
        del shipment_gen
    return shipment_ids


def get_shipment_detail_util(shipment_id, user_email):
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
        print(res.headers, type(res.headers), res.headers.get('retry-after', 10))
        raise RateLimitException(res.headers.get('retry-after', '30'))
    else:
        return res.json()

@task
def save_shipments(shipment, user_email, pk):
    """saving collected shipments data"""
    try:
        with transaction.atomic():
            # for shipment in data['shipments']:
            shipment_items = shipment.pop('shipmentItems')
            transport = shipment.pop('transport')
            customer_details = shipment.pop('customerDetails')
            billing_details = shipment.pop('billingDetails')

            # saving shipment items
            for item in shipment_items:
                item.update({'shipment': pk})
                sh_item_serializer = ShipmentItemSerializer(data=item)
                if sh_item_serializer.is_valid():
                    sh_item_serializer.save()
                else:
                    log_bolo.error(sh_item_serializer.errors)

            # saving transport of shipment
            transport.update({'shipment': pk})
            transport_serializer = TransportSerializer(data=transport)
            if transport_serializer.is_valid():
                transport_serializer.save()
            else:
                print(transport_serializer.errors)
                log_bolo.error(transport_serializer.errors)

            # saving customer details of shipment
            customer_details.update({'shipment': pk})
            cust_serializer = CustomerDetailsSerializer(data=customer_details)
            if cust_serializer.is_valid():
                cust_serializer.save()
            else:
                print(cust_serializer.errors)
                log_bolo.error(cust_serializer.errors)

            # saving billing details of shipment
            billing_details.update({'shipment': pk})
            bill_details_serializer = BillingDetailsSerializer(data=billing_details)
            if bill_details_serializer.is_valid():
                bill_details_serializer.save()
            else:
                print(bill_details_serializer.errors)
                log_bolo.error(bill_details_serializer.errors)

    except (DatabaseError, KeyError, TypeError) as e:
        raise e

@task
def get_shipment_details(sh_id, user_email, pk):
    try:
        sh_details = get_shipment_detail_util(sh_id, user_email)
        return sh_details
    except RateLimitException as e:
        exp_data = e.retry_after
        print(">>>> retrying after <<<<", exp_data)
        get_shipment_details.retry(countdown=int(e.retry_after), exc=e)

@task
def error_handler(uuid):
    result = AsyncResult(uuid)
    print(uuid, result)




