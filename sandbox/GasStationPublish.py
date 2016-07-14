"""
Gas Station Simulator Publisher
===============================

A simple example how to read information from a kafka topic and place
it on


Requirements
------------

:requires: kafka (https://github.com/dpkp/kafka-python)
:requires: flask
:requires: flask-restful (http://flask-restful-cn.readthedocs.io/en/0.3.5/quickstart.html)


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 6-Jul-2016
"""
import numpy as np
from flask import Flask
from flask_restful import Resource, Api
from kafka import KafkaConsumer
import datetime

# set up kafka
topic = 'gasStation'
consumer1 = KafkaConsumer(topic)
consumer2 = KafkaConsumer(topic)

# set up Flask and the API
app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {'hello': '%s' % datetime.datetime.now()}


class Location(Resource):
    def get(self):
        return {'lat': 51.45 + 0.1*np.random.random(),
                'long': -0.1 + 0.1*np.random.random()}


class Update(Resource):
    def get(self):
        partitions = consumer1.poll(timeout_ms=100)
        if len(partitions) > 0:
            return {'msg': '%s' % datetime.datetime.now()}
        else:
            return {'msg': 'no new data'}


class Streaming(Resource):
    def get(self):
        partitions = consumer2.poll(timeout_ms=1000)
        tmp = []
        if len(partitions) > 0:
            for p in partitions:
                for response in partitions[p]:
                    tmp.append(response.value.decode("utf-8"))
        return{'msg': tmp}


api.add_resource(HelloWorld, '/')
api.add_resource(Update, '/update/')
api.add_resource(Streaming, '/stream/')
api.add_resource(Location, '/location/')


if __name__ == '__main__':
    app.run(debug=True)
