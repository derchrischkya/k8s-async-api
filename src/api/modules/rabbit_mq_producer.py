import pika
import time

class Producer:
    def __init__(self, host, port, username, password, virtual_host, timeout=10):
        try:
            connection_params = pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(username, password),
                virtual_host=virtual_host)
            self.connection = pika.BlockingConnection(connection_params)
            self.connection.call_later(timeout, self.on_timeout)
            self.channel = self.connection.channel()
        except Exception as ex:
            raise ConnectionError(f"Error connecting to RabbitMQ: {ex}")
        
    def produce(self, exchange, routing_key, body, key=None, reply_queue=None):
        try:
            if reply_queue is None:
                reply_queue = self.channel.queue_declare(queue='', exclusive=True).method.queue
        
            self.channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    reply_to=reply_queue,
                    correlation_id=key
                )
            )
        except Exception as ex:
            raise ConnectionError(f"Error producing response-message: {ex}")

    def return_reply_queue(self, queue_name, exclusive=True):
        reply_queue = self.channel.queue_declare(queue=queue_name, exclusive=exclusive)
        return reply_queue.method.queue
    
    def declare_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name, durable=True)
        
    def consume(self, queue_name):
        try:
            self.channel.basic_consume(queue=queue_name,
                                    on_message_callback=self.on_message_received)
            self.channel.start_consuming()
        except TimeoutError as ex:
            raise TimeoutError(f"Timeout consume response data from queue")
        except Exception as ex:
            raise ConnectionError(f"Connection to RabbitMQ as consumer failed: {ex}")

    def close(self):
        self.channel.close()
        self.connection.close()
            
    def on_timeout(self):
        self.close()
        raise TimeoutError("")

    
    def on_message_received(self, ch, method, properties, body):
        print("Received message:", body)
        # Process the received message here
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.close()
