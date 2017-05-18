#! /usr/bin/env python

from PIL import Image
import random

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

    def save_to_file(self, uuid):
        with open(uuid+".png",'w') as fp:
            self.image.save(fp, "PNG")

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
        print('Got task: {0!r}'.format(task))

        juliaset = JuliaSet(task['width'],
                            task['height'],
                            task['xa'],
                            task['xb'],
                            task['ya'],
                            task['yb'],
                            task['iterations'])
        juliaset.save_to_file(task['uuid'])
        message.ack()

connection = Connection('amqp://guest:guest@localhost:5672//')
server = Worker(connection)
try:
        server.run()
except KeyboardInterrupt:
        pass
