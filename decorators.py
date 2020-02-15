from functools import wraps
from flask import jsonify
from http import HTTPStatus

ALLOWED_MIMETYPES = {'image/png', 'image/jpeg'}


def allowed_mimetypes(func):
    @wraps(func)
    def decorated(message, *args, **kwargs):
        return func(message, *args, **kwargs)

    return decorated
