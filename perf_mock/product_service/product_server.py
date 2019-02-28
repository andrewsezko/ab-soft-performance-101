#!flask/bin/python

from flask import Flask, jsonify, request
from requests import get
from time import sleep
from random import randrange
import os
import json

# Extract server config from env vars
PRODUCT_SERVER_HOST = os.getenv('PRODUCT_SERVER_HOST', '0.0.0.0')
PRODUCT_SERVER_PORT = os.getenv('PRODUCT_SERVER_PORT', '7777')
AUTH_SERVER_HOST = os.getenv('AUTH_SERVER_HOST', '0.0.0.0')
AUTH_SERVER_PORT = os.getenv('AUTH_SERVER_PORT', '7778')

# Pseudo throttling params setup
SLOWDOWN_SERVICE_MS_MIN = int(os.getenv('SLOWDOWN_SERVICE_MS_MIN', 50))
SLOWDOWN_SERVICE_MS_MAX = int(os.getenv('SLOWDOWN_SERVICE_MS_MAX', 500))


def slowdown(min_ms=SLOWDOWN_SERVICE_MS_MIN, max_ms=SLOWDOWN_SERVICE_MS_MAX, random_step_ms=50):
    sleep_time = randrange(min_ms, max_ms, random_step_ms) / 1000.0
    sleep(sleep_time)


app = Flask(__name__)


def init_db():
    with open('products.json') as f:
        return json.load(f)


PRODUCTS_DB = init_db()  # in-memory storage for products, will be flushed after server reload


def validate_token(token):
    req_url = "http://{}:{}/api/auth/validate_token/{}".format(AUTH_SERVER_HOST, AUTH_SERVER_PORT, token)
    app.logger.info("Validating token: {}".format(req_url))
    res = get(req_url)
    if res.ok:
        if res.json()['status'] == 'ok':
            return True

    return False


def user_token_is_valid():
    if 'token' in request.cookies:
        token = request.cookies.get('token')
        return validate_token(token)

    return False


@app.route('/api/products/get_all', methods=['GET'])
def get_all_products():
    slowdown()
    if user_token_is_valid() is False:
        return jsonify({'status': 'ko', 'message': 'No valid user token in request'}), 401

    return jsonify(PRODUCTS_DB)


@app.route('/api/products/get_product/<string:product_id>', methods=['GET'])
def get_product(product_id):
    slowdown()
    if user_token_is_valid() is False:
        return jsonify({'status': 'ko', 'message': 'No valid user token in request'}), 401

    for product in PRODUCTS_DB:
        if product_id == product['_id']:
            return jsonify({'status': 'ok', 'product': product})
    return jsonify({'status': 'ko', 'message': 'No such product'})


@app.errorhandler(Exception)
def unhandled_exception(e):
    return jsonify({'error': str(e), 'status': 'ko'}), 500


if __name__ == '__main__':
    try:
        app.run(debug=False, host=PRODUCT_SERVER_HOST, port=PRODUCT_SERVER_PORT)
    except Exception as ex:
        print("Error occurred: {}".format(str(ex)))
    finally:
        exit()
