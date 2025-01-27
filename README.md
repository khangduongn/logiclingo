# LogicLingo

## Setting up your python virtual environment

1. Create a new Python virtual environment

```python -m venv </path/to/new/virtual/environment>```

2. Activate the virtual environment

```source </path/to/new/virtual/environment>/bin/activate```

3. Install the required Python modules using the provided requirements.txt file

```pip install -r </path/to/requirements.txt>```

NOTE: Remember to activate your virtual environment before you start developing

## Setting up the app
3. Clone this repository using ```git clone``` and then ```cd``` into the directory

4. ```cd``` into the logiclingo directory which should contain the files settings.py and urls.py

5. Create a new file called ```.env``` in this directory with the following environment variables with the appropriate credentials that match your PostgreSQL database credentials

SECRET_KEY= \<DJANGO_SECRET_KEY>\
DB_NAME= \<YOUR_DB_NAME>\
DB_USER= \<YOUR_DB_USERNAME>\
DB_PASSWORD= \<YOUR_DB_PASSWORD>\
DB_HOST= \<YOUR_DB_HOST>\
DB_PORT= \<YOUR_DB_PORT>

6. If you want to run the app, enter this command and follow the output instruction to access the website (make sure that you are in the same directory as the ```manage.py``` file when running this command) \
```python manage.py runserver``` 

7. If you make changes to the models (database schema), make sure to make migrations or else your changes won't be saved (make sure that you are in the same directory as the ```manage.py``` file when running these commands) \
```python manage.py makemigrations``` \
```python manage.py migrate```

