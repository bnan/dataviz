import os
import json
import requests
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, send_from_directory, jsonify, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__, static_url_path='')

app.config.update(
    DATABASE=os.path.join(app.root_path, 'hackenei.db'),
    DEBUG=False,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
)


################################################################################
# Database
################################################################################

def db_connect():
    """Connects to the specific database."""
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = dict_factory

    return rv

def db_init():
    """Initializes the database."""
    db = db_open()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command()
def initdb():
    db_init()
    print('Initialized the database.')


def db_open():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = db_connect()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

################################################################################
# Intersections
################################################################################

def intersection_exists(street0, street1):
    db = db_open()
    cur = db.execute('SELECT * FROM intersections WHERE street0=? AND street1=?', (street0, street1))
    results1 = cur.fetchall()

    cur = db.execute('SELECT * FROM intersections WHERE street0=? AND street1=?', (street1, street0))
    results2 = cur.fetchall()

    return (len(results1) + len(results2)) > 0

def intersection_add(street0, street1, point):
    db = db_open()
    lat, lon = point
    db.execute('INSERT INTO intersections (street0, street1, lat, lon) VALUES (?, ?, ?, ?)', (street0, street1, lat, lon))
    db.commit()

def intersection_get(city, street0, street1):
    res = {}

    if not intersection_exists(street0, street1):

        app_id = 'zTZ7lW4XZ8JTo1mYccMi'
        app_code = 'U9s3ZGxyK9wTP3wEgldk2w'
        url = 'https://geocoder.cit.api.here.com/6.2/geocode.json?city=' + city + '&street0=' + street0 + '&street1=' + street1 + '&app_id=' + app_id + '&app_code=' + app_code + '&gen=9'

        r = requests.get(url)
        res = r.json()
        view = res['Response']['View']
        position = res['Response']['View'][0]['Result'][0]['Location']['DisplayPosition']
        position = position['Latitude'], position['Longitude']
        intersection_add(street0, street1, position)

    db = db_open()
    cur = db.execute('SELECT * FROM intersections WHERE street0=? AND street1=?', (street0, street1))
    results = cur.fetchall()

    if len(results) == 0:
        cur = db.execute('SELECT * FROM intersections WHERE street0=? AND street1=?', (street1, street0))
        results = cur.fetchall()
    return results[0]['lat'], results[0]['lon']

def traffic_get_all(city, start="", end=""):
    traffic = []

    url = 'http://data.hackenei.citibrain.com/api/traffic/?start='+start+'&end='+end+'&group_by=day'
    print(url)
    r = requests.get(url)

    res = r.json()
    for x in res['results']:
        c1 = intersection_get(city, x['roadway_name'], x['roadway_segment_start'])
        c2 = intersection_get(city, x['roadway_name'], x['roadway_segment_end'])
        temp = { "coordinates" : [(c1[0] + c2[0])/2.0,(c1[1] + c2[1])/2.0], "count" : x['count'], "name" : x['roadway_name'], "date" : x['day'] }
        traffic.append(temp)

    while res['next']:
        r = requests.get(res['next'])
        res = r.json()
        for x in res['results']:
            print(x)
            c1 = intersection_get(city, x['roadway_name'], x['roadway_segment_start'])
            c2 = intersection_get(city, x['roadway_name'], x['roadway_segment_end'])
            temp = { "coordinates" : [(c1[0] + c2[0])/2.0,(c1[1] + c2[1])/2.0], "count" : x['count'], "name" : x['roadway_name'], "date" : x['day'] }
            traffic.append(temp)

    return traffic

################################################################################
# API Endpoints
################################################################################

@app.route('/api', methods=['GET'])
def api():
    #req = request.get_json(force=True)
    date_start = request.args.get('date_start') #req['date_start']
    date_end = request.args.get('date_end') #req['date_end']

    traffic = traffic_get_all('New York',date_start, date_end)
    res = {'points': traffic }

    return jsonify(**res)

################################################################################
# Client
################################################################################

@app.route('/')
def client_index():
    return open('../client/hack.html').read()

@app.route('/scripts/<path:path>')
def client_scripts(path):
    return send_from_directory('../client/scripts', path)

@app.route('/styles/<path:path>')
def client_styles(path):
    return send_from_directory('../client/styles', path)

@app.route('/images/<path:path>')
def client_images(path):
    return send_from_directory('../client/images', path)

@app.route('/fonts/<path:path>')
def client_fonts(path):
    return send_from_directory('../client/fonts', path)


if __name__ == "__main__":
    app.run()
