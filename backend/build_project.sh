#!/bin/bash

ROOT_DIR=$(pwd)
SCRIPT_DIR=$ROOT_DIR/pugorugh/scripts

echo Starting in $ROOT_DIR
echo Scripts directory $SCRIPT_DIR

echo Run makemigrations
python manage.py makemigrations

echo Run migrate
python manage.py migrate

echo Importing data
cd $SCRIPT_DIR ; python data_import.py

echo Process complete, run \"python manage.py runserver\" from $ROOT_DIR
