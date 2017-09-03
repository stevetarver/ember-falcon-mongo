FROM python:3.6.2-alpine3.6

COPY app/ /app/
COPY requirements.txt /app/
COPY constraints.txt /app/
COPY build/docker-entrypoint.sh /docker-entrypoint.sh

RUN apk add --no-cache bash && \
    pip install -r /app/requirements.txt

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]