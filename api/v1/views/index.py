#!/usr/bin/python3
"""Gets and returns the status of the api."""
from flask import jsonify, request
from api.v1.views import app_views
from models import storage


@app_views.route("/status", methods=['GET'], strict_slashes=False)
def status():
    """Return the status of the API, in json format."""
    if request.method == 'GET':
        return jsonify({"status": "OK"})


@app_views.route("/stats", methods=['GET'], strict_slashes=False)
def stats():
    """Retrieve the number of each objects by type."""
    if request.method == 'GET':
        classes = {
            "amenities": "Amenity",
            "cities": "City",
            "places": "Place",
            "reviews": "Review",
            "states": "State",
            "users": "User"
        }
        counts = {key: storage.count(value) for key, value in classes.items()}
        return jsonify(counts)
