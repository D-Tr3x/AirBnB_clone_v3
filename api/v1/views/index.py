#!/usr/bin/python3
"""Gets and returns the status of the api"""
from flask import jsonify, request
from api.v1.views import app_views


@app_views.route("/status", methods=['GET'], strict_slashes=False)
def status():
    """Returns the status of the API, in json format"""
    if request.method == 'GET':
        return jsonify({"status": "OK"})
