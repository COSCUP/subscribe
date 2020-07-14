docker run -d --restart='always' \
           --name secretary-1 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:5999:6699 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           secretary-app:prod python3 ./main.py

docker run -d --restart='always' \
           --name secretary-2 \
           --link secretary_mongo:mongo \
           --link queue_sender:rabbitmq \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:5998:6699 \
           -e LD_PRELOAD=/usr/local/lib/libjemalloc.so \
           secretary-app:prod python3 ./main.py
