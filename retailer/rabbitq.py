import pika

parameters = pika.URLParameters('amqp://srujan:srujan123@localhost:5672')
conn = pika.BlockingConnection(parameters)


class RabbitMQ:
    def __init__(self):
        self.conn = None
        self.url = 'amqp://srujan:srujan123@localhost:5672'

    def get_new_connection(self):
        self.conn = pika.BlockingConnection(self.url)
        return self.conn

    def check_connection(self):
        return self.conn.is_open
