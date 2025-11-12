#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

if [ "${LOAD_SAMPLE_DATA:-false}" = "true" ]; then
  python create_fresh_test_data.py
fi

exec "$@"

