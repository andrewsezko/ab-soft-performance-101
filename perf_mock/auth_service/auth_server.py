#!flask/bin/python

from flask import Flask, jsonify
from random import randrange
from time import sleep
from uuid import uuid4
import os

# Extract server config from env vars
AUTH_SERVER_HOST = os.getenv('AUTH_SERVER_HOST', '0.0.0.0')
AUTH_SERVER_PORT = os.getenv('AUTH_SERVER_PORT', '7778')

# Pseudo throttling params setup
SLOWDOWN_SERVICE_MS_MIN = int(os.getenv('SLOWDOWN_SERVICE_MS_MIN', 50))
SLOWDOWN_SERVICE_MS_MAX = int(os.getenv('SLOWDOWN_SERVICE_MS_MAX', 500))


def slowdown(min_ms=SLOWDOWN_SERVICE_MS_MIN, max_ms=SLOWDOWN_SERVICE_MS_MAX, random_step_ms=50):
    sleep_time = randrange(min_ms, max_ms, random_step_ms) / 1000.0
    sleep(sleep_time)


app = Flask(__name__)

TOKENS = []  # in-memory storage for user tokens, will be flushed after server reload


@app.route('/api/auth/generate_token', methods=['GET'])
def generate_token():
    slowdown()
    token = str(uuid4())
    TOKENS.append(token)
    app.logger.info("Generated token: {}".format(token))
    return jsonify({'token': token}), 200


@app.route('/api/auth/validate_token/<string:token_id>', methods=['GET'])
def validate_token(token_id):
    slowdown()
    if token_id in TOKENS:
        return jsonify({'status': 'ok'}), 200
    else:
        return jsonify({'status': 'ko'}), 400


@app.errorhandler(Exception)
def unhandled_exception(e):
    return jsonify({'error': str(e), 'status': 'ko'}), 500


if __name__ == '__main__':
    try:
        app.run(debug=False, host=AUTH_SERVER_HOST, port=AUTH_SERVER_PORT)
    except Exception as ex:
        print("Error occurred: {}".format(str(ex)))
    finally:
        exit()
