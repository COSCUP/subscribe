docker run \
           -it --rm \
           --name secretary-worker \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/scripts:/app/scripts \
           -e PYTHONPATH=/app \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           secretary-app:prod sh
