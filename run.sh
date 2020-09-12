#!/bin/sh

cd /src
# If started in Fargate, the env variable with payload is set
# If not, start uwsgi server for lambda
if [[ "$ACTINGWEB_PAYLOAD" != "" ]]; then
    python application.py
else
    uwsgi uwsgi.ini
fi
