docker run \
           -it --rm \
           --name secretary-worker \
           --link secretary_mongo:mongo \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/scripts:/app/scripts \
           -e PYTHONPATH=/app \
           secretary-app:prod sh
