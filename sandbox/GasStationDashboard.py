"""
Gas Station Simulator Dashboard
===============================

A simple example how to read information from a kafka topic and place
it on a website. The web page will show a rolling log.


Requirements
------------

:requires: flask (http://flask.pocoo.org)
:requires: kafka (https://github.com/dpkp/kafka-python)


Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 6-Jul-2016
"""
from kafka import KafkaConsumer
from flask import Flask
from flask import Response
from flask import json
from flask import jsonify


app = Flask(__name__)


@app.route('/log/', methods=['GET'])
def output(topic='gasStation'):
    consumer = KafkaConsumer(topic)
    #consumer = KafkaConsumer(topic, value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    def generate():
        for msg in consumer:
            yield json.dumps(msg.value.decode("utf-8"))
            #yield jsonify(msg.value.decode("utf-8"))

    #return Response(generate(), mimetype='text/csv')
    return Response(generate(), status=200, mimetype='application/json')


@app.route('/stream', methods=['GET'])
def stream(topic='gasStation'):
    consumer = KafkaConsumer(topic)

    tmp = []
    for msg in consumer:
        tmp.append(msg.value.decode("utf-8"))

    return Response(jsonify(tmp), status=200, mimetype='application/json')


if __name__ == "__main__":
    app.run(debug=True)
