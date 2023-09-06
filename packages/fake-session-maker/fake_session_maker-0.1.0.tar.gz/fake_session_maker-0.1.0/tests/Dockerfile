FROM python:3
LABEL authors="dturba"

ENTRYPOINT ["top", "-b"]

# install postgres
RUN apt-get update && apt-get install -y postgresql postgresql-contrib
# create user and database
RUN service postgresql start &&\
    su - postgres -c "psql -c \"CREATE USER test WITH PASSWORD 'test';\"" &&\
    su - postgres -c "psql -c \"CREATE DATABASE test OWNER test;\"" &&\
    su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE test TO test;\""
