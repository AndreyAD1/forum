FROM python:3.9-alpine

RUN adduser -D forum

WORKDIR /home/forum

COPY requirements-prod.txt .
RUN  apk add --no-cache postgresql-libs && \
     apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
     python -m venv venv && \
     venv/bin/pip install -r requirements-prod.txt && \
     apk --purge del .build-deps

COPY app app
COPY migrations migrations
COPY forum.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP forum.py

RUN chown -R forum:forum ./
USER forum

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]