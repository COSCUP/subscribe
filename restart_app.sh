sh ./build-app.sh

docker stop -t 1 secretary_celery
docker rm secretary_celery

sh ./start_celery.sh

docker stop -t 1 secretary-1
docker rm secretary-1

sh ./start_app.sh
