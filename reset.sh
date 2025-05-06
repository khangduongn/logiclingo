#!/bin/bash

# Drop and recreate database
psql postgres -c "DROP DATABASE IF EXISTS logiclingo;"
psql postgres -c "CREATE DATABASE logiclingo;"

# Grant privileges - this is crucial for migrations to work
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE logiclingo TO \"$USER\";"
psql logiclingo -c "GRANT ALL PRIVILEGES ON SCHEMA public TO \"$USER\";"

# Run Django migrations
python3 manage.py makemigrations
python3 manage.py migrate