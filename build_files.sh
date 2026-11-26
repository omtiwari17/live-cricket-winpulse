#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
