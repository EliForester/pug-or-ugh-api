#  Pug or Ugh

Backend django rest framework for existing project

## Getting Started

Clone the repository, activate virtual environment and/or make sure all requirements are installed

#### From script

From the project's root directory run this bash script, it will run DB migrations and populate the database

```
./build_project.sh
```

#### Manually

From the top backend directory

```
python manage.py makemigrations
python manage.py migrate
cd pugorugh/scripts
python data_import.py
```

#### Run app

```
python manage.py runserver
```

### Prerequisites

Created on Python 3

requirements.txt
```
coverage==4.5.2
Django==1.9.9
djangorestframework==3.4.1
```

## Test coverage

With migrations omitted

```
Name                      Stmts   Miss  Cover
---------------------------------------------
backend/__init__.py           0      0   100%
backend/settings.py          21      0   100%
backend/urls.py               4      0   100%
manage.py                     6      0   100%
pugorugh/__init__.py          0      0   100%
pugorugh/admin.py             1      0   100%
pugorugh/models.py           52     19    63%
pugorugh/serializers.py      45     20    56%
pugorugh/tests.py           112      1    99%
pugorugh/urls.py              7      0   100%
pugorugh/views.py            94     16    83%
---------------------------------------------
TOTAL                       342     56    84%
```

## Running the tests

From pug_or_ugh_api/backend directory

```
python manage.py test
```

Or with coverage

```
coverage run manage.py test
coverage report
```
