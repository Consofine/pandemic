from flask import render_template, redirect, g, Flask, request, url_for, session
from sqlite3 import dbapi2 as sqlite3
from os import path
import requests
app = Flask(__name__)


app.config.from_pyfile('config.py')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db_file = app.config["DATABASE"]
        exists = path.isfile(db_file)
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        if not exists:
            qry = open('schema.sql', 'r').read()
            c = db.cursor()
            c.executescript(qry)
            db.commit()
            c.close()

    # Make sure database has tables
    return db



