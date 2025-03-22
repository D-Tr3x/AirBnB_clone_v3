#!/usr/bin/python3
"""Implements all default RESTful API actions for Review objects."""
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET', 'POST'],
                 strict_slashes=False)
def reviews_by_place(place_id):
    """
    Handle requests for Review objects associated with a specific Place.

    GET:
        - Retrieves the list of all Review objects for the given place.
        - If the place_id is not linked to any Place, raises a 404 error.
    POST:
        - Creates a new Review for the given place.
        - Expects a JSON body; if invalid,
          raises a 400 error with "Not a JSON".
        - If the JSON body does not contain the key "user_id",
          raises a 400 error with "Missing user_id".
        - If the JSON body does not contain the key "text",
          raises a 400 error with "Missing text".
        - Returns the new Review object in JSON format with status 201.
    """
    place = storage.get(Place, place_id)
    if place is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        if hasattr(place, 'reviews'):
            reviews_list = [review.to_dict() for review in place.reviews]
        else:
            all_reviews = storage.all(Review).values()
            reviews_list = [review.to_dict() for review in all_reviews
                            if review.place_id == place_id]
        return jsonify(reviews_list)

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
        if "text" not in json_data:
            return make_response(jsonify({"error": "Missing text"}), 400)
        json_data['place_id'] = place_id
        new_review = Review(**json_data)
        storage.new(new_review)
        storage.save()
        return jsonify(new_review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['GET', 'PUT', 'DELETE'],
                 strict_slashes=False)
def reviews_by_id(review_id=None):
    """
    Handle requests for a specific Review object by its ID.

    GET:
        - Retrieves the Review object with the given review_id.
        - If review_id is not linked to any Review, raises a 404 error.
    PUT:
        - Updates the Review object with the given review_id.
        - Expects a JSON body; if invalid, raises 400 error with "Not a JSON".
        - Updates the Review object with all key-value pairs provided.
        - Ignores keys: id, user_id, place_id, created_at, updated_at.
        - Returns updated Review object in JSON format, with 200 status code.
    DELETE:
        - Deletes the Review object with the given review_id.
        - If the review_id is not linked to any Review, raises a 404 error.
        - Returns an empty dictionary with a 200 status code.
    """
    review = storage.get(Review, review_id)
    if review is None:
        abort(404, 'Not found')

    if request.method == 'GET':
        return jsonify(review.to_dict())

    if request.method == 'PUT':
        if not request.is_json:
            return make_response(jsonify({"error": "Not a JSON"}), 400)
        json_data = request.get_json(silent=True)
        if not json_data:
            return make_response(jsonify({"error": "Not a JSON"}), 400)

        for key, value in json_data.items():
            if key not in [
                    'id', 'user_id', 'place_id', 'created_at', 'updated_at']:
                setattr(review, key, value)
        storage.save()
        return jsonify(review.to_dict()), 200

    if request.method == 'DELETE':
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
