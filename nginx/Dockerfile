FROM nginx:1.25.2-alpine

COPY ./nginx.conf /etc/nginx/nginx.conf

RUN apk update && \
    apk upgrade && \
    apk --update add logrotate

COPY logrotate/nginx /etc/logrotate.d

RUN apk add --no-cache curl

RUN mkdir /subscribe_cache

RUN set -x ; \
    addgroup -g 82 -S www-data ; \
    adduser -u 82 -D -S -G www-data www-data && exit 0 ; exit 1

RUN rm /etc/nginx/conf.d/default.conf

CMD [ "nginx" ]

EXPOSE 80 443