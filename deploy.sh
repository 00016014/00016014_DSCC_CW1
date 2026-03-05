#!/bin/bash
cd ~/00016014_DSCC_CW1
git pull origin main
docker compose pull
docker compose down
docker compose up -d
sleep 10
docker compose exec -T web python manage.py makemigrations core
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py collectstatic --noinput
echo 'Deployment complete!'