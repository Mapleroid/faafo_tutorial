#! /usr/bin/env python

from PIL import Image
import random
import tempfile
import time
import os
import base64
import hashlib
import json
import socket
import requests

from kombu import Queue, Exchange, Connection
from kombu.mixins import ConsumerMixin

class JuliaSet(object):

    def __init__(self, width, height, xa=-2.0, xb=2.0, ya=-1.5, yb=1.5,
                 iterations=255):
        self.xa = xa
        self.xb = xb
        self.ya = ya
        self.yb = yb
        self.iterations = iterations
        self.width = width
        self.height = height
        self.draw()

    def draw(self):
        self.image = Image.new("RGB", (self.width, self.height))
        c, z = self._set_point()
        for y in range(self.height):
            zy = y * (self.yb - self.ya) / (self.height - 1) + self.ya
            for x in range(self.width):
                zx = x * (self.xb - self.xa) / (self.width - 1) + self.xa
                z = zx + zy * 1j
                for i in range(self.iterations):
                    if abs(z) > 2.0:
                        break
                    z = z * z + c
                self.image.putpixel((x, y),
                                    (i % 8 * 32, i % 16 * 16, i % 32 * 8))

    #def save_to_file(self, uuid):
    #    with open(uuid+".png",'w') as fp:
    #        self.image.save(fp, "PNG")
    def get_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            self.image.save(fp, "PNG")
            return fp.name

    def _set_point(self):
        random.seed()
        while True:
            cx = random.random() * (self.xb - self.xa) + self.xa
            cy = random.random() * (self.yb - self.ya) + self.ya
            c = cx + cy * 1j
            z = c
            for i in range(self.iterations):
                if abs(z) > 2.0:
                    break
                z = z * z + c
            if i > 10 and i < 100:
                break

        return (c, z)

class Worker(ConsumerMixin):
    task_queue = Queue('julia_queue', Exchange('julia_exchange',type='direct'), 'julia_generate')

    def __init__(self, connection):
        self.connection = connection

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[self.task_queue],
                         accept=['json'],
                         callbacks=[self.on_task])]

    def on_task(self, task, message):
        #print('Got task: {0!r}'.format(task))
        start_time = time.time()

        juliaset = JuliaSet(task['width'],
                            task['height'],
                            task['xa'],
                            task['xb'],
                            task['ya'],
                            task['yb'],
                            task['iterations'])
        elapsed_time = time.time() - start_time

        #juliaset.save_to_file(task['uuid'])
        filename = juliaset.get_file()
        with open(filename, "rb") as fp:
            size = os.fstat(fp.fileno()).st_size
            image = base64.b64encode(fp.read())
        checksum = hashlib.sha256(open(filename, 'rb').read()).hexdigest()
        os.remove(filename)
        
        result = {
            'uuid': task['uuid'],
            'duration': elapsed_time,
            'image': image,
            'checksum': checksum,
            'size': size,
            'generated_by': socket.gethostname()
        }

        # NOTE(berendt): only necessary when using requests < 2.4.2
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

        requests.put("%s/v1/fractal/%s" %
                     ('http://localhost:5000', str(task['uuid'])),
                     json.dumps(result), headers=headers)

        message.ack()
        return result


connection = Connection('amqp://guest:guest@localhost:5672//')
server = Worker(connection)
try:
        server.run()
except KeyboardInterrupt:
        pass
