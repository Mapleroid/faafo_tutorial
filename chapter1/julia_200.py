#! /usr/bin/env python

from PIL import Image
from datetime import datetime
import random
import uuid

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

def get_random_task():
    random.seed()

    width = random.randint(256,1024)
    height = random.randint(256,1024)
    iterations = random.randint(128,512)
    xa = random.uniform(-1.0,-4.0)
    xb = random.uniform(1.0,4.0)
    ya = random.uniform(-0.5,-3)
    yb = random.uniform(0.5,3)
    id=str(uuid.uuid4())

    juliaset = JuliaSet(width, height, xa, xb, ya, yb, iterations)
    juliaset.save_to_file(id)


def job():
    start_time=datetime.now()
    for i in range(0,200):
        get_random_task()

    execute_time=datetime.now()-start_time
    print execute_time

job()

