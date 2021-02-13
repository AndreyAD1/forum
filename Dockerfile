FROM python:3.9-alpine

RUN adduser -D forum

WORKDIR /home/forum

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY forum.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP forum.py

RUN chown -R forum:forum ./
USER forum

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]