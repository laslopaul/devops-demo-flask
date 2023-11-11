#!/bin/sh
set -e

flask db init
gunicorn --bind=0.0.0.0:8000 devops-demo-app:app
