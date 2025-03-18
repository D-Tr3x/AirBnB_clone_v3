#!/usr/bin/python3
"""Implements all default RESTful API actions for Amenity objects."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.amenity import Amenity


@app_views.route('/amenities', methods=['GET', 'POST'], strict_slashes=False)
def amenities_no_id():
    """
    Handle requests without a amenity ID.

    GET:
        - Retrieves the list of all Amenity objects.
    POST:
        - Creates a new Amenity.
        - Expects a JSON body; if invalid,
          returns a 400 error with "Not a JSON".
        - If the JSON body does not contain the key "name", return a 400 error.
        - Return the new Amenity object in JSON format, with status code 201.
    """
    if request.method == 'GET':
        amenities = storage.all(Amenity).values()
        amenities_list = [amenity.to_dict() for amenity in amenities]
        return jsonify(amenities_list)

    if request.method == 'POST':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)

        json_data = request.get_json(force=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        if "name" not in json_data:
            return make_response(jsonify({"error": "Missing name"}), 400)
        new_amenity = Amenity(**json_data)
        storage.new(new_amenity)
        storage.save()
        return jsonify(new_amenity.to_dict()), 201


@app_views.route('/amenities/<amenity_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def amenities_with_id(amenity_id=None):
    """
    Handle requests with a amenity ID.

    GET:
        - Retrieves the Amenity object with the given amenity_id.
        - If not found, returns a 404 error.
    PUT:
        - Updates the Amenity object with the given amenity_id.
        - Expects a JSON body; if invalid, returns a 400 error.
        - Ignores keys: id, created_at, updated_at.
        - Returns the updated Amenity object in JSON format with 200 status.
    DELETE:
        - Deletes the Amenity object with the given amenity_id.
        - If not found, return a 404 error.
        - Returns an empty dictionary and a 200 status code.
    """
    amenity = storage.get(Amenity, amenity_id)
    if amenity is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(amenity.to_dict())

    if request.method == 'PUT':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        for key, value in json_data.items():
            if key not in ['id', 'created_at', 'updated_at']:
                setattr(amenity, key, value)
        storage.save()
        return jsonify(amenity.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(amenity)
        storage.save()
        return jsonify({}), 200
