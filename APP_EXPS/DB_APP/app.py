"""
HTML generated from data pulled from a database.

In this example we're pulling data from a simple sqlite3 database and
building an HTML template with it.

Requirements:
 * A database created with some data about authors inside.
"""
from flask import Flask, g, render_template, request, flash, redirect, url_for, send_from_directory
import config  # type: ignore
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Required for flash messages

# Add route to serve Bootstrap files from shared directory
@app.route('/bootstrap/<path:filename>')
def bootstrap_static(filename):
    bootstrap_dir = os.path.join(os.path.dirname(__file__), '..', 'bootstrap')
    return send_from_directory(bootstrap_dir, filename)

def connect_db():
    return sqlite3.connect(config.DATABASE_NAME)

@app.before_request
def before_request():
    '''
    Connect to the database before the following any request is handled.
    Would enable multiple queries per request (or helper-function) if needed.
    '''
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    '''
    Close the database connection at the end of every request.
    This ensures connections are properly cleaned up, even if an error occurs.
    '''
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    if exception:
        # Log the exception if needed
        print(f"Request ended with exception: {exception}")

@app.route('/', methods=['POST', 'GET'])
def hello_world():
    if request.method == 'POST':
        # Clean and validate input
        author_name = request.form.get('author', '').strip()
        country_name = request.form.get('country', '').strip()
        
        # Remove extra spaces between words
        author_name = ' '.join(author_name.split())
        country_name = ' '.join(country_name.split())
        
        # Apply title case for consistent formatting
        author_name = author_name.title()
        country_name = country_name.title()
        
        # Validation checks
        if not author_name or not country_name:
            flash('Please fill in both Author Name and Country fields.', 'error')
        elif len(author_name) > 100:
            flash('Author name is too long (maximum 100 characters).', 'error')
        elif len(country_name) > 100:
            flash('Country name is too long (maximum 100 characters).', 'error')
        elif len(author_name) < 2:
            flash('Author name is too short (minimum 2 characters).', 'error')
        elif len(country_name) < 2:
            flash('Country name is too short (minimum 2 characters).', 'error')
        else:
            # Check if country exists, if not insert it
            country_cursor = g.db.execute('SELECT id FROM country WHERE name = ?', (country_name,))
            country_row = country_cursor.fetchone()
            
            try:
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
            except sqlite3.Error as e:
                flash(f'Database error: {str(e)}', 'error')
                g.db.rollback()
        
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

@app.route('/delete/<int:author_id>', methods=['POST'])
def delete_author(author_id):
    # Get author name for flash message before deleting
    cursor = g.db.execute('SELECT name FROM author WHERE id = ?', (author_id,))
    author = cursor.fetchone()
    
    if author:
        author_name = author[0]
        g.db.execute('DELETE FROM author WHERE id = ?', (author_id,))
        g.db.commit()
        flash(f'Author "{author_name}" deleted successfully.', 'success')
    else:
        flash('Author not found.', 'error')
    
    return redirect(url_for('hello_world'))

if __name__ == '__main__':
	app.debug = True
	host = os.environ.get('IP', '0.0.0.0')
	port = int(os.environ.get('PORT', 8080))
	app.run(host=host, port=port)