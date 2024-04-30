#!/usr/bin/env python

from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
import time
import uuid
from modules.logger import Logger
from modules.rabbit_mq_producer import Producer
from modules.state_db_sqlite import SQLLITE
import json
import os

class Body(BaseModel):
    message: str


class AsyncResponse(BaseModel):
    timestamp: str | None = time.strftime("%Y-%m-%d %H:%M:%S%z")
    redirect_uri: str | None = ""
    msg: str | None = ""
    is_async: bool | None = True

class CustomResponse(BaseModel):
    timestamp: str | None = time.strftime("%Y-%m-%d %H:%M:%S%z")
    msg: str | None = ""
    completed: bool | None = True

## Some CONSTANTS (for PROD dont save passwords in code!)

DISPATCHER_QUEUE = "dispatcher-queue"
 
app = FastAPI()

@app.post("/ping", status_code=202)
async def send_message(body: Body, response: Response) -> AsyncResponse:
    try:
        log = Logger()
        log.info(f"Waiting to awnser: {body.message}")
        id = str(uuid.uuid4())
        queue_name = DISPATCHER_QUEUE
        producer = Producer(os.getenv("RABBITMQ_HOST"),
                            os.getenv("RABBITMQ_PORT"),
                            os.getenv("RABBITMQ_USER"),
                            os.getenv("RABBITMQ_PASS"),
                            os.getenv("RABBITMQ_VHOST"))
        reply_queue = producer.return_reply_queue("", exclusive=True)
        producer.declare_queue(queue_name)
        log.info(f"Sending request {id} to queue {queue_name}")
        producer.produce(
            "", queue_name, key=id, body="", reply_queue=reply_queue
        )
        log.info(f"Wait for response on queue {reply_queue}")
        producer.consume(reply_queue)
        log.info(f"Response received for request {id}")
        
        response = AsyncResponse(
            redirect_uri=f"/state/{id}",
            msg="Waiting for response message from the server may take some time, grab a coffee and relax",)
        log.debug(response)
        return response
    except TimeoutError as ex:
        log.error(f"Timeout error occured: {ex}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {body.message}")
    except ConnectionError as ex:
        log.error(f"Connection error occured: {ex}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {body.message}")
    except Exception as ex:
        log.error(f"Error creating index {body.message} - {ex}")
        raise HTTPException(status_code=500, detail=f"Error sending message: {body.message}")
    

@app.get("/state/{id}", status_code=200)
async def get_state_from_db(id: str, response: Response):
    try:
        log = Logger()
        log.info(f"Getting state for {id}")
        db = SQLLITE("./state/requests.db")
        # Get the message from the database
        # SELECT message, completed, requester, timestamp, queue FROM requests WHERE id=?", (id,))
            
        message = db.get(id)
        db.close()
        if message is None:
            raise ValueError(f"Item {id} not found")
        
        log.info(f"Message: {message}")
        completed = True
        msg = message[0]
        
        if message[1] == 0:
            completed = False
            msg = "The request is still in progress"
            
        return CustomResponse(msg=msg, completed=completed)
    except ValueError as ex:
        log.error(f"Error getting state for {id} - {ex}")
        response.status_code = status.HTTP_404_NOT_FOUND
    except Exception as ex:
        log.error(f"Error getting state for {id} - {ex}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
