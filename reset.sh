sudo -u postgres psql -c "DROP DATABASE logiclingo;"
sudo -u postgres psql -c "CREATE DATABASE logiclingo;"
python3 manage.py makemigrations
python3 manage.py migrate