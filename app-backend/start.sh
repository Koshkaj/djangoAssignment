#!/bin/sh

set -eux

# gunicorn -w 4 -b 0.0.0.0:8080 backend.wsgi # Production

python3 manage.py runserver 0.0.0.0:8080
