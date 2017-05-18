#! /usr/bin/env python
from kombu import Connection, Producer, Exchange

import json
import random
import uuid
import random

def get_random_task():
    random.seed()


    width = random.randint(256,1024)

    height = random.randint(256,1024)

    iterations = random.randint(128,512)

    xa = random.uniform(-1.0,-4.0)

    xb = random.uniform(1.0,4.0)

    ya = random.uniform(-0.5,-3)

    yb = random.uniform(0.5,3)

    task = {
        'uuid': str(uuid.uuid4()),
        'width': width,
        'height': height,
        'iterations': iterations, 'xa': xa,
        'xb': xb,
        'ya': ya,
        'yb': yb
    }

    return task

exchange = Exchange('julia_exchange', type='direct')

with Connection('amqp://guest:guest@localhost:5672//') as connection:
    producer = Producer(connection)
    producer.publish(get_random_task(),
                     exchange=exchange,
                     routing_key='julia_generate',
                     serializer='json',
                     compression='zlib')
