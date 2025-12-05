"""
HTML generated from data pulled from a database.

In this example we're pulling data from a simple sqlite3 database and
building an HTML template with it.

Requirements:
 * A database created with some data about authors inside.
"""
from flask import Flask, g, render_template, request, flash, redirect, url_for
import config  # type: ignore
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Required for flash messages

def connect_db():
    return sqlite3.connect(config.DATABASE_NAME)

@app.before_request
def before_request():
    '''
    Connect to the database before the following any request is handled.
    Would enable multiple queries per request (or helper-function) if needed.
    '''
    g.db = connect_db()    

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        # Clean and validate input
        author_name = request.form.get('author', '').strip()
        country_name = request.form.get('country', '').strip()
        
        # Skip if either field is empty after stripping
        if not author_name or not country_name:
            flash('Please fill in both Author Name and Country fields.', 'error')
        else:
            # Check if country exists, if not insert it
            country_cursor = g.db.execute('SELECT id FROM country WHERE name = ?', (country_name,))
            country_row = country_cursor.fetchone()
            
            if country_row is None:
                # Country doesn't exist, insert it
                g.db.execute('INSERT INTO country (name) VALUES (?)', (country_name,))
                g.db.commit()
                # Get the newly inserted country's id
                country_id = g.db.execute('SELECT last_insert_rowid()').fetchone()[0]
            else:
                # Country exists, use its id
                country_id = country_row[0]
            
            # Check if author already exists
            author_cursor = g.db.execute('SELECT id FROM author WHERE name = ?', (author_name,))
            author_row = author_cursor.fetchone()
            
            if author_row is None:
                # Author doesn't exist, insert them
                g.db.execute('INSERT INTO author (name, country_id) VALUES (?, ?)',
                             (author_name, country_id))
                g.db.commit()
                flash(f'Author "{author_name}" from {country_name} added successfully!', 'success')
            else:
                # If author exists, show info message
                flash(f'Author "{author_name}" already exists in the database.', 'info')
        
        return redirect(url_for('hello_world'))
    
    # GET request continues here (either direct visit or after redirect)
    cursor = g.db.execute('''
                        SELECT a.id, a.name, c.name as country
                        FROM author AS a
                            INNER JOIN country AS c ON a.country_id = c.id
                        ORDER BY a.name;
                        ''')
    authors = [dict(id=row[0], name=row[1], country=row[2]) for row in cursor.fetchall()]
    return render_template('authors_with_form.html', authors=authors)

if __name__ == '__main__':
	app.debug = True
	host = os.environ.get('IP', '0.0.0.0')
	port = int(os.environ.get('PORT', 8080))
	app.run(host=host, port=port)