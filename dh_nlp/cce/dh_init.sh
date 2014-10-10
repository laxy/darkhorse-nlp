#!/bin/sh
sudo mongod &
memcached &

python populate_db.py
python classifier.py
python recommendation_engine.py

