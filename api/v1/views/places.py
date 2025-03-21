#!/usr/bin/python3
"""Implements all default RESTful API actions for Place objects."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET', 'POST'],
                 strict_slashes=False)
def places_by_city(city_id):
    """
    Handle requests for Place objects associated with a specific City.

    GET:
        - Retrieves the list of all Place objects for the given state.
        - If the city_id is not linked to any City, raises a 404 error.
    POST:
        - Creates a new Place for the given state.
        - Expects a JSON body; if invalid,
          raises a 400 error with "Not a JSON".
        - If the JSON body does not contain the key "name",
          raises a 400 error with "Missing name".
        - Returns the new Place object in JSON format with status 201.
    """
    city = storage.get(City, city_id)
    if city is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        if hasattr(city, 'places'):
            places_list = [place.to_dict() for place in city.places]
        else:
            all_places = storage.all(Place).values()
            places_list = [place.to_dict() for place in all_places
                           if place.place_id == place_id]
        return jsonify(places_list)

    if request.method == 'POST':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if "user_id" not in json_data:
            return make_response(jsonify({"error": "Missing user_id"}), 400)
        if storage.get(User, json_data["user_id"]) is None:
            abort(404, 'Not found')
        if "name" not in json_data:
            return make_response(jsonify({"error": "Missing name"}), 400)
        json_data['city_id'] = city_id
        new_place = Place(**json_data)
        storage.new(new_place)
        storage.save()
        return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def places_by_id(place_id=None):
    """
    Handle requests for a specific Place object by its ID.

    GET:
        - Retrieves the Place object with the given place_id.
        - If place_id is not linked to any Place, raises a 404 error.
    PUT:
        - Updates the Place object with the given place_id.
        - Expects a JSON body; if invalid, raises 400 error with "Not a JSON".
        - Updates the Place object with all key-value pairs provided.
        - Ignores keys: id, place_id, created_at, updated_at.
        - Returns updated Place object in JSON format, with 200 status code.
    DELETE:
        - Deletes the Place object with the given place_id.
        - If the place_id is not linked to any Place, raises a 404 error.
        - Returns an empty dictionary with a 200 status code.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(place.to_dict())

    if request.method == 'PUT':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)

        for key, value in json_data.items():
            if key not in [
                    'id', 'user', 'place_id', 'created_at', 'updated_at']:
                setattr(place, key, value)
        storage.save()
        return jsonify(place.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(place)
        storage.save()
        return jsonify({}), 200
