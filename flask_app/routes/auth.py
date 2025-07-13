import datetime
import jwt
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app
from db.models import User
from utils.data_validation import UserValidator
from pydantic import ValidationError
from errors.exceptions import AuthError
import logging

auth = Blueprint('auth', __name__)

def authorization(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json(silent=True)
        if not data:
            logging.warning('No input data received')
            raise AuthError("No input data received")
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            logging.warning('User didnt provide email or password')
            raise AuthError("Please provide email and password")
        s = g.db
        user = s.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            g.user_id = user.id
            return f(*args, **kwargs)
        else:
            raise AuthError()
    return decorated


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        logging.warning('No data received')
        raise AuthError("Provide email and password.")
    try:
        user = UserValidator(email=data.get('email'), password=data.get('password'), name=data.get('name'))
        s = g.db
        exists = s.query(User).filter_by(email=data.get('email')).first()
        if exists:
            raise AuthError("Email already registered")
        new_user = User(email = user.email, name = user.name)
        new_user.set_password(user.password)
        s.add(new_user)
    except ValidationError as e:
        return jsonify({'message': str(e)}), 400
    logging.info('New user registered')
    return jsonify({'message':f'Success, registered email: {user.email}'}), 201


@auth.route('/get_token', methods=['POST'])
@authorization
def get_token():
    payload = {
        'user_id': g.user_id,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=10)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token}), 200



