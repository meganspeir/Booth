from flask import Flask, render_template
from capture.database import db_session

app = Flask(__name__)

app.config.from_object('config')


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()

import capture.views
