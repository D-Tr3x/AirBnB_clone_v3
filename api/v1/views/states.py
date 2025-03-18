#!/usr/bin/python3
"""Implements all default RESTful API actions for State."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET', 'POST'], strict_slashes=False)
def states_no_id():
    """
    Handle requests without a state ID.

    GET:
        - Retrieves the list of all State objects.
    POST:
        - Creates a new State.
        - Expects a JSON body; if missing or invalid, retiurns 400.
    """
    if request.method == 'GET':
        states = storage.all(State).values()
        states_list = [state.to_dict() for state in states]
        return jsonify(states_list)

    if request.method == 'POST':
        try:
            json_data = request.get_json(force=True)
        except Exception:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if json_data is None:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if json_data.get("name") is None:
            return make_response(jsonify({"error": "Missing name"}), 400)
        new_state = State(**json_data)
        storage.new(new_state)
        storage.save()
        return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def states_with_id(state_id=None):
    """
    Handle requests with a state ID.

    GET:
        - Retrieves the State objects with the given ID.
        - If not found, returns a 404 error.
    PUT:
        - Updates the State object with the given ID.
        - Expects a JSON body; if missing or invalid, retiurns 400.
        - Ignores keys: id, created_at, updated_at.
    DELETE:
        - Deletes the State object with the given ID.
        - Returns an empty dictionary and a 200 status code.
    """
    state = storage.get(State, state_id)
    if state is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(state.to_dict())

    if request.method == 'PUT':
        try:
            json_data = request.get_json()
        except Exception:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if json_data is None:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        for key, value in json_data.items():
            if key not in ['id', 'created_at', 'updated_at']:
                setattr(state, key, value)
        storage.save()
        return jsonify(state.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(state)
        storage.save()
        return jsonify({}), 200
