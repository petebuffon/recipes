#!/bin/bash

export SECRET_KEY=$(python3 -c "import os; print(os.urandom(16))")

gunicorn -c /config/gunicorn.conf.py recipes:app
