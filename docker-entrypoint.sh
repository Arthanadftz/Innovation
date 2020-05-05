#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status
set -x  # all executed commands are printed to the terminal.

export PYTHONUNBUFFERED=0

case "$1" in
    check)
        python manage.py check
        exec prospector --profile .prospector.yaml
    ;;
    test)
        exec python manage.py test "${@:2}"
    ;;
    runserver)
        echo starting gunicorn...
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        exec python manage.py runserver 0.0.0.0:8000
    ;;
    web)
        echo starting gunicorn...
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        exec /usr/local/bin/gunicorn innovation.wsgi -b 0.0.0.0:8000 -w 8
    ;;
    jupyter)
        exec jupyter notebook --allow-root --config=jupyter_config/jupyter_notebook_config.py
    ;;
    *)
        exec $@
     ;;
esac
