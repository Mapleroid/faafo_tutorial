#! /usr/bin/env python
from kombu import Connection, Producer, Exchange

import flask
import flask_restless
import flask_sqlalchemy
from sqlalchemy.dialects import mysql
import uuid


app = flask.Flask('faafo.api')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://faafo:password@localhost/faafo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = flask_sqlalchemy.SQLAlchemy(app)

class Fractal(db.Model):
    uuid = db.Column(db.String(36), primary_key=True)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    iterations = db.Column(db.Integer, nullable=False)
    xa = db.Column(db.Float, nullable=False)
    xb = db.Column(db.Float, nullable=False)
    ya = db.Column(db.Float, nullable=False)
    yb = db.Column(db.Float, nullable=False)

    checksum = db.Column(db.String(256), unique=True)
    url = db.Column(db.String(256), nullable=True)
    duration = db.Column(db.Float)
    size = db.Column(db.Integer, nullable=True)
    generated_by = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return '<Fractal %s>' % self.uuid

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    image_uuid = db.Column(db.String(36), db.ForeignKey('fractal.uuid'))
    image = db.Column(mysql.MEDIUMBLOB, nullable=True)

    def __repr__(self):
        return '<Image %s>' % self.uuid


db.create_all()
manager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

def generate_fractal(**kwargs):
    with Connection('amqp://guest:guest@localhost:5672//') as connection:
        producer = Producer(connection)
        producer.publish(kwargs['result'],
                     exchange=Exchange('julia_exchange', type='direct'),
                     routing_key='julia_generate',
                     serializer='json',
                     compression='zlib')

if __name__ == "__main__":
    manager.create_api(Fractal, methods=['GET', 'POST', 'DELETE', 'PUT'],
                    postprocessors={'POST': [generate_fractal]},
                    url_prefix='/v1')
    manager.create_api(Image, methods=['GET', 'POST', 'DELETE', 'PUT'],
                       url_prefix='/v1')
    app.run(host="0.0.0.0", port=5000)
