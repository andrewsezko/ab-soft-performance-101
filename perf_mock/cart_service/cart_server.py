#!flask/bin/python

from flask import Flask, jsonify, request
from random import randrange
from requests import get
from time import sleep
import os

# Extract server config from env vars
PRODUCT_SERVER_HOST = os.getenv('PRODUCT_SERVER_HOST', '0.0.0.0')
PRODUCT_SERVER_PORT = os.getenv('PRODUCT_SERVER_PORT', '7777')

AUTH_SERVER_HOST = os.getenv('AUTH_SERVER_HOST', '0.0.0.0')
AUTH_SERVER_PORT = os.getenv('AUTH_SERVER_PORT', '7778')

CART_SERVER_HOST = os.getenv('CART_SERVER_HOST', '0.0.0.0')
CART_SERVER_PORT = os.getenv('CART_SERVER_PORT', '7779')

# Pseudo throttling params setup
SLOWDOWN_SERVICE_MS_MIN = int(os.getenv('SLOWDOWN_SERVICE_MS_MIN', 50))
SLOWDOWN_SERVICE_MS_MAX = int(os.getenv('SLOWDOWN_SERVICE_MS_MAX', 500))


def slowdown(min_ms=SLOWDOWN_SERVICE_MS_MIN, max_ms=SLOWDOWN_SERVICE_MS_MAX, random_step_ms=50):
    sleep_time = randrange(min_ms, max_ms, random_step_ms) / 1000.0
    sleep(sleep_time)


app = Flask(__name__)

CART = {}


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


def product_exists(product_id):
    slowdown()
    req_url = "http://{}:{}/api/products/get_product/{}".format(PRODUCT_SERVER_HOST, PRODUCT_SERVER_PORT, product_id)
    app.logger.info("Checking if product exists: {}".format(req_url))

    cookies = request.cookies
    app.logger.info("Added cookies: {}".format(str(cookies)))
    res = get(req_url, cookies=cookies)

    if res.ok:
        if res.json()['status'] == 'ok':
            return True

    return False


@app.route('/api/cart/add_item/<string:product_id>', methods=['GET'])
def add_item_to_cart(product_id):
    slowdown()
    if user_token_is_valid() is False:
        return jsonify({'status': 'ko', 'message': 'No valid user token in request'}), 401
    user_token = request.cookies.get('token')

    if product_exists(product_id) is True:
        if user_token in CART:
            user_cart = CART[user_token]
            user_cart.append(product_id)
        else:
            CART[user_token] = [product_id]
    else:
        return jsonify({'status': 'ko', 'message': 'No such product'}), 404

    return jsonify({'status': 'ok', 'message': 'Product added to cart'}), 200


@app.route('/api/cart/get_items', methods=['GET'])
def get_cart_items():
    slowdown()
    if user_token_is_valid() is False:
        return jsonify({'status': 'ko', 'message': 'No valid user token in request'}), 401

    user_token = request.cookies.get('token')
    cart_items = []
    if user_token in CART:
        cart_items = CART[user_token]

    return jsonify({'status': 'ok', 'cart_items': cart_items})


@app.route('/api/cart/checkout', methods=['GET'])
def checkout():
    slowdown()
    if user_token_is_valid() is False:
        return jsonify({'status': 'ko', 'message': 'No valid user token in request'}), 401

    user_token = request.cookies.get('token')
    if user_token in CART:
        del CART[user_token]
        return jsonify({'status': 'ok'}), 200
    else:
        return jsonify({'status': 'ko', 'message': 'Cart is empty, nothing to checkout'}), 400


@app.errorhandler(Exception)
def unhandled_exception(e):
    return jsonify({'error': str(e), 'status': 'ko'}), 500


if __name__ == '__main__':
    try:
        app.run(debug=False, host=CART_SERVER_HOST, port=CART_SERVER_PORT)
    except Exception as ex:
        print("Error occurred: {}".format(str(ex)))
    finally:
        exit()
