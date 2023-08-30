docker run -d --restart='always' \
           --name secretary-1 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:5999:5000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           secretary-app:prod poetry run uwsgi ./uwsgi.ini

docker run -d --restart='always' \
           --name secretary-2 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:5998:5000 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           secretary-app:prod poetry run uwsgi ./uwsgi.ini
