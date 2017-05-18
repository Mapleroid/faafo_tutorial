#! /usr/bin/env python

import requests
import uuid
import json
import random

headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

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
        'iterations': iterations, 
        'xa': xa,
        'xb': xb,
        'ya': ya,
        'yb': yb
    }

    return task

# add a item
#requests.post("%s/v1/fractal" % "http://localhost:5000",
#              json.dumps(get_random_task()),headers=headers)

# add some items
#for i in range(0,100):
#    requests.post("%s/v1/fractal" % "http://localhost:5000",
#              json.dumps(get_random_task()),headers=headers)
 

# update a item
#requests.put("%s/v1/fractal/%s" % ("http://localhost:5000",'f0e3480e-60f9-42e9-9769-cd7dd62dd138'),
#              json.dumps({'username':'test3'}),headers=headers)

# delete a item
#requests.delete("%s/v1/fractal/%s" % ("http://localhost:5000",'f0e3480e-60f9-42e9-9769-cd7dd62dd138'),
#                 headers=headers)

# get a item
#result = requests.get("%s/v1/fractal/%s" % ("http://localhost:5000",'a2746f2b-c905-4389-a8e0-e758749f0b35'),
#                 headers=headers)

#if result.status_code == 200:
#    print result.text

# get all items
#response = requests.get("%s/v1/fractal" % "http://localhost:5000",
#                 headers=headers)


# query
#filters = [dict(name='size', op='gt',val=0)]
#filters = [dict(name='checksum', op='is_not_null')]
filters = [dict({"and": [dict(name='size', op='gt',val=0),dict(name='checksum', op='is_not_null')]})]
params = dict(q=json.dumps(dict(filters=filters)))

response = requests.get("%s/v1/fractal%s" % ("http://localhost:5000","?page=2&results_per_page=5"), params=params, headers=headers)

#response = requests.get("%s/v1/fractal/%s" % ("http://localhost:5000",'99c06c4c-6253-4a91-bdbe-f48037997169'),
#                 headers=headers)
print response.status_code
print(response.json())
