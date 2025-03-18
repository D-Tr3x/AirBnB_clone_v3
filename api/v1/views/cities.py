#!/usr/bin/python3
"""Implements all default RESTful API actions for City objects."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.state import State
from models.city import City


@app_views.route('/states/<state_id>/cities', methods=['GET', 'POST'],
                 strict_slashes=False)
def cities_by_state(state_id):
    """
    Handle requests for City objects associated with a specific State.

    GET:
        - Retrieves the list of all City objects for the given state.
        - If the state_id is not linked to any State, raises a 404 error.
    POST:
        - Creates a new City for the given state.
        - Expects a JSON body; if invalid,
          raises a 400 error with "Not a JSON".
        - If the JSON body does not contain the key "name",
          raises a 400 error with "Missing name".
        - Returns the new City object in JSON format with status 201.
    """
    state = storage.get(State, state_id)
    if state is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        cities = []
        if hasattr(state, 'cities'):
            state_cities = [city.to_dict() for city in state.cities]
        else:
            all_cities = storage.all(City).values()
            state_cities = [city.to_dict() for city in all_cities
                            if city.state_id == state_id]
        return jsonify(state_cities)

    if request.method == 'POST':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if json_data.get("name") is None:
            return make_response(jsonify({"error": "Missing name"}), 400)
        json_data['state_id'] = state_id
        new_city = City(**json_data)
        storage.new(new_city)
        storage.save()
        return jsonify(new_city.to_dict()), 201


@app_views.route('/cities/<city_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def cities_with_id(city_id=None):
    """
    Handle requests for a specific City object by its ID.

    GET:
        - Retrieves the City objects with the given city_id.
        - If city_id is not linked to any City, raises a 404 error.
    PUT:
        - Updates the City object with the given city_id.
        - Expects a JSON body; if invalid, raises 400 error with "Not a JSON".
        - Updates the City object with all key-value pairs provided.
        - Ignores keys: id, state_id, created_at, updated_at.
        - Returns the updated City object in JSON format, with 200 status code.
    DELETE:
        - Deletes the City object with the given city_id.
        - If the city_id is not linked to any City, raises a 404 error.
        - Returns an empty dictionary with a 200 status code.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(city.to_dict())

    if request.method == 'PUT':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)

        for key, value in json_data.items():
            if key not in ['id', 'state_id', 'created_at', 'updated_at']:
                setattr(city, key, value)
        storage.save()
        return jsonify(city.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(city)
        storage.save()
        return jsonify({}), 200
