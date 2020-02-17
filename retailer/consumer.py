from django.conf import settings
import os
import json
import pika
from .views.shipment_util import get_util, shipment_details_util, save_shipments_util

parameters = pika.URLParameters('amqp://srujan:srujan123@localhost:5672')
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='retailer')
channel.queue_declare(queue='shipmentid')
channel.queue_declare(queue='shipment')


def retailer_callback(ch, method, properties, body):
    str_body = body.decode('utf-8')
    shipment_ids = get_util(str_body)
    for shipment_id in shipment_ids:
        channel.basic_publish(exchange='', routing_key='shipmentid', body=str(shipment_id)+','+str_body)


def shipmentid_callback(ch, method, properties, body):
    str_body = body.decode('utf-8')
    shipment_id, user_email = str_body.split(',')
    shipment_detail = shipment_details_util(shipment_id, user_email)
    channel.basic_publish(exchange='', routing_key='shipment',
                          body=json.dumbs({'shipment_detail': shipment_detail, 'user_email': user_email}))


def shipment_callback(ch, method, properties, body):
    str_body = body.decode('utf-8')
    json_body = json.loads(str_body)
    save_shipments_util(json_body['shipment_detail'], json_body['user_email'])


channel.basic_consume(queue='retailer', on_message_callback=retailer_callback, auto_ack=True)
channel.basic_consume(queue='shipmentid', on_message_callback=shipmentid_callback, auto_ack=True)
channel.basic_consume(queue='shipment', on_message_callback=shipment_callback, auto_ack=True)


def start_consuming():
    channel.start_consuming()


print(">>> Waiting for messages <<<")
start_consuming()
