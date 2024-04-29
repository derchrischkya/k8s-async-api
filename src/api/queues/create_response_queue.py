#!/opt/homebrew/bin//python3
import sys
import os
import asyncio
import aio_pika


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
from modules.state_db_sqlite import SQLLITE

class INDEX_QUEUE:
    async def create_index(self, seconds):
        await asyncio.sleep(seconds)

    async def __on_request_message_received(self, message):
        async with message.process():
            # Store the request in the persist database
            print(f"Request received: {message.correlation_id}")
            print(f"Message: {message.body}")
            await self.create_index(10)  # Await the create_index call
            db = SQLLITE("../state/requests.db")
            db.update(
                message.correlation_id,
                completed=True,
                message="pong",
            )
            print(f"The state in the database {message.correlation_id} was updated")


    async def consume(self, connection, queue_name):
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(queue_name, durable=True)
            async for message in queue:
                asyncio.create_task(self.__on_request_message_received(message))


async def main():
    connection = await aio_pika.connect_robust(
        host=os.getenv("RABBITMQ_HOST"),
        port=int(os.getenv("RABBITMQ_PORT")),
        login=os.getenv("RABBITMQ_USER"),
        password=os.getenv("RABBITMQ_PASS"),
        virtualhost=os.getenv("RABBITMQ_VHOST")
    )
    server = INDEX_QUEUE()
    queue_name = "pong-queue"
    await server.consume(connection, queue_name)


if __name__ == "__main__":
    asyncio.run(main())
