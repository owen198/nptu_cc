

from flask import Flask, render_template, request, jsonify, make_response, json, send_from_directory, redirect, url_for
import pika
import logging
import warnings

# packages for swagger
from flasgger import Swagger
from flasgger import swag_from

# setup flask app
app = Flask(__name__)

# setup swagger online document
swagger = Swagger(app)

# setup logger
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

# create user restful API
@app.route('/create_user', methods=['POST'])
@swag_from('apidocs/api_create_user.yml')
def create_user():

    # retrive post body
    jsonobj = request.get_json(silent=True)
    username = json.dumps(jsonobj['username']).replace("\"", "")
    password = json.dumps(jsonobj['password']).replace("\"", "")

    logging.info('username:', username)
    logging.info('password:', password)

    message = dict()
    message['username'] = username
    message['password'] = password

    # push username and password
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)
    #message = ' '.join(sys.argv[1:]) or "NPTU Cloud Computing"

    message = json.dumps(message)
    logging.info('message:', message)

    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(delivery_mode=2)
    )

    connection.close()

    # reture requests
    res = dict()
    res['success'] = True
    res['message'] = 'Create user successed, your username=' + username
    res = make_response(jsonify(res), 200)
    return res



@app.route('/')
def index():
    return 'Web App with Python Flask!'


if __name__ =='__main__':
    app.run(host='0.0.0.0', port=5000)
