#!/usr/bin/python3
"""Implements all default RESTful API actions for User objects."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.user import User


@app_views.route('/users', methods=['GET', 'POST'], strict_slashes=False)
def users_no_id():
    """
    Handle requests without a user user_id.

    GET:
        - Retrieves the list of all User objects.
    POST:
        - Creates a new User.
        - Expects a JSON body; if invalid,
          returns a 400 error with "Not a JSON".
        - If the JSON body does not contain the key "email",
          return a 400 error with "Missing email".
        - If the JSON body does not contain the key "password",
          return a 400 error with "Missing password".
        - Return the new User object in JSON format, with status code 201.
    """
    if request.method == 'GET':
        users = storage.all(User).values()
        users_list = [user.to_dict() for user in users]
        return jsonify(users_list)

    if request.method == 'POST':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)

        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if "email" not in json_data:
            return make_response(jsonify({"error": "Missing email"}), 400)
        if "password" not in json_data:
            return make_response(jsonify({"error": "Missing password"}), 400)
        new_user = User(**json_data)
        storage.new(new_user)
        storage.save()
        return jsonify(new_user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def users_with_id(user_id=None):
    """
    Handle requests with a user user_id.

    GET:
        - Retrieves the User object with the given user_id.
        - If not found, returns a 404 error.
    PUT:
        - Updates the User object with the given user_id.
        - Expects a JSON body; if invalid, returns a 400 error.
        - Updates the User object with all key-value pairs.
        - Ignores keys: id, email, created_at, updated_at.
        - Returns the updated User object in JSON format with 200 status.
    DELETE:
        - Deletes the User object with the given user_id.
        - If not found, return a 404 error.
        - Returns an empty dictionary and a 200 status code.
    """
    user = storage.get(User, user_id)
    if user is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(user.to_dict())

    if request.method == 'PUT':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        for key, value in json_data.items():
            if key not in ['id', 'email', 'created_at', 'updated_at']:
                setattr(user, key, value)
        storage.save()
        return jsonify(user.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
