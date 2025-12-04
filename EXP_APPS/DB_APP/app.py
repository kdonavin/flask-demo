"""
HTML generated from data pulled from a database.

In this example we're pulling data from a simple sqlite3 database and
building an HTML template with it.

Requirements:
 * A database created with some data about authors inside.
"""
from flask import Flask, g, render_template
import config  # type: ignore
import os
import sqlite3

app = Flask(__name__)

def connect_db():
    return sqlite3.connect(config.DATABASE_NAME)

# @app.before_request
# def before_request():
#     g.db = connect_db()    

@app.route('/')
def hello_world():
    db_connection = connect_db()
    cursor = db_connection.execute('''
                                    SELECT id, name, country_id 
                                   FROM author
                                   ORDER BY name;
                                   ''')
    authors = [dict(id=row[0], name=row[1], country_id=row[2]) for row in cursor.fetchall()]
    return render_template('authors.html', authors=authors)

if __name__ == '__main__':
	app.debug = True
	host = os.environ.get('IP', '0.0.0.0')
	port = int(os.environ.get('PORT', 8080))
	app.run(host=host, port=port)