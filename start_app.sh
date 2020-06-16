docker run -d --restart='always' \
           --name secretary-1 \
           --log-opt max-size=64m \
           --log-opt max-file=1 \
           -v $(pwd)/log:/app/log \
           -p 127.0.0.1:5999:6699 \
           secretary-app:prod python3 ./main.py
