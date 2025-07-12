from functools import wraps
import jwt
from flask import request, jsonify, g, current_app


def token_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.headers.get('Authorization')
        if not data or not data.startswith('Bearer '):
            return jsonify({'message': 'Invalid Authorization field'}), 401
        token = data.split(' ')[1]
        try:
            payload =jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'] )
            g.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return func(*args, **kwargs)
    return wrapper

