#! /usr/bin/env python

from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import requests
import json
import flask
import base64
import cStringIO
from PIL import Image

template_path = "/home/crack/faafo_tutorial/chapter9/templates"
app = Flask('faafo.web', template_folder=template_path)
Bootstrap(app)

def get_page(page=1):
    headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

    filters = [dict({"and": [dict(name='size', op='gt',val=0),dict(name='checksum', op='is_not_null')]})]
    params = dict(q=json.dumps(dict(filters=filters)))
    
    response = requests.get("%s/v1/fractal?page=%d&results_per_page=%d" % ("http://localhost:5000",page,5), params=params, headers=headers)

    return response    


'''
 A fake class to using render_pagination

 # .has_prev        bool
 # .prev_num        int 
 # .iter_pages()    func
 # .page            object
 # .has_next
 # .next_num
 # .items

'''
class Paginate(object):
    def __init__(self,response):
        self.page = response['page']
        self.pages = response['total_pages']
        self.items = response['objects']
    
    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_num(self):
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_num(self):
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
        


app.route('/')
@app.route('/index')
@app.route('/index/<int:page>', methods=['GET'])
def index(page=1):
    fractals = get_page(page).json()
    paginate = Paginate(fractals)

    return render_template('index.html', fractals=paginate)


def _get_fractal(fractalid):
    headers = {'Content-type': 'application/json',
                   'Accept': 'text/plain'}

    filters = [dict(name='image_uuid', op='eq',val=fractalid)]
    params = dict(q=json.dumps(dict(filters=filters)))
    response = requests.get("%s/v1/image" % "http://localhost:5000", params=params, headers=headers)    

    if response.status_code != 200:
        return None

    return response.json()['objects'][0]

@app.route('/fractal/<string:fractalid>', methods=['GET'])
def get_fractal(fractalid):
    fractal = _get_fractal(fractalid)

    if not fractal:
        response = flask.jsonify({'code': 404,
                                  'message': 'Fracal not found'})
        response.status_code = 404
    else:
        image_data = base64.b64decode(fractal['image'])
        image = Image.open(cStringIO.StringIO(image_data))
        output = cStringIO.StringIO()
        image.save(output, "PNG")
        image.seek(0)
        response = flask.make_response(output.getvalue())
        response.content_type = "image/png"

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080,debug=True)
