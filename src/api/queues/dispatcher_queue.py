#!/opt/homebrew/bin//python3
import sys
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
import pika
from modules.state_db_sqlite import SQLLITE


class SERVER:
    def __get_state_from_db(self, id):
        db = SQLLITE("../state/requests.db")
        message = db.get(id)
        db.close()
        return message

    def __store_state_in_db(
        self,
        id,
        message,
        completed=False,
        requester="async-api",
        timestamp="",
        queue="",
    ):
        db = SQLLITE("../state/requests.db")
        db.insert(id, message, completed, requester, timestamp, queue)
        db.close()

    def __on_request_message_received(self, ch, method, properties, body):
        # Store the request in the persist database
        print(f"Request received: {properties.correlation_id}")
        self.__store_state_in_db(
            id=properties.correlation_id,
            message=body,
            completed=False,
            requester="async-api",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S%z"),
            queue=method.routing_key
        )
        print(f"The reply_to is {properties.reply_to}")

        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            body=f"It is your request {properties.correlation_id}",
        )
        
        ## Key - Queue Routing
        ch.basic_publish(
            exchange="",
            routing_key="pong-queue",
            body=body,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            )
        )
        

    def __init__(self, host, port, username, password, virtual_host):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                virtual_host=virtual_host,
            )
        )
        self.channel = self.connection.channel()

    def declare_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)

    def consume(self, queue_name):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.__on_request_message_received,
            auto_ack=True,
        )
        self.channel.start_consuming()

server = SERVER(
    host=os.getenv("RABBITMQ_HOST"),
    port=os.getenv("RABBITMQ_PORT"),
    username=os.getenv("RABBITMQ_USER"),
    password=os.getenv("RABBITMQ_PASS"),
    virtual_host=os.getenv("RABBITMQ_VHOST")
)
queue_name = "dispatcher-queue"
server.declare_queue(queue_name)
server.consume(queue_name)
