#!/bin/sh

set -e

python manage.py wait_for_db
python manage.py collectstatic --noinput
python manage.py migrate

/usr/bin/supervisord -c /etc/supervisord.conf