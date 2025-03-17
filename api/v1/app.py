#!/usr/bin/python3
"""
This module starts a Flask web application.

The application registers the `app_views` blueprint,
sets up the teardown method for closing the storage session,
and runs the Flask server using environment variables for configuration.
"""


from flask import Flask
from models import storage
from api.v1.views import app_views
import os


app = Flask(__name__)
app.register_blueprint(app_views)


@app.teardown_appcontext
def teardown_db(exception):
    """Close storage after each request."""
    storage.close()


if __name__ == "__main__":
    """Runs the Flask application."""
    host = os.getenv("HBNB_API_HOST", "0.0.0.0")
    port = int(os.getenv("HBNB_API_PORT", "5000"))
    app.run(host=host, port=port, threaded=True)
