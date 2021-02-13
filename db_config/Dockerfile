FROM postgres:13.2-alpine

ARG forum_db_user
ARG forum_db_password
ENV FORUM_DB_USER=$forum_db_user
ENV FORUM_DB_PASSWORD=$forum_db_password
COPY initialize_db.sh /docker-entrypoint-initdb.d/initialize_db.sh