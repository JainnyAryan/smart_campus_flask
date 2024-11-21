from functools import wraps
from firebase_admin import auth
from flask import jsonify, request, g


def protected_route(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        id_token = request.headers.get('Authorization')
        if not id_token:
            return jsonify({"message": "Authorization token missing"}), 401

        if id_token.startswith("Bearer "):
            id_token = id_token.split(" ")[1]

        try:
            decoded_token = auth.verify_id_token(id_token=id_token)
            request.user = decoded_token
        except Exception as e:
            return jsonify({"message": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return decorated_function
