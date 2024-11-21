from flask import jsonify


def handle_error(exception):
    return jsonify({"message": str(exception)}), 500
