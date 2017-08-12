FROM python:3.6.2

COPY app/ /app/
COPY requirements.txt /app/
COPY constraints.txt /app/
COPY docker-entrypoint.sh /docker-entrypoint.sh

RUN pip install -r /app/requirements.txt

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]