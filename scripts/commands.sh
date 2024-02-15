#!/bin/sh

set -e

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST $POSTGRES_PORT) ..."
  sleep 2
done

echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"

while ! nc -z redis $REDIS_PORT; do
  echo "🟡 Waiting for Redis Startup (redis $REDIS_PORT) ..."
  sleep 2
done

echo "✅ Redis Started Successfully (redis:$REDIS_PORT)"

python manage.py collectstatic --noinput
# mc cp --recursive ./static_files minio/local-static
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py runserver 0.0.0.0:8000
