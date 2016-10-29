export FLASK_APP=server.py
flask initdb
flask run --host=0.0.0.0 --port=1337
