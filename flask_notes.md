# Flask

Flask is a web micro-framework. It provides you with the minimal tools and libraries to build a web application in Python. It is a micro-framework because it only has 2 dependencies

* Werkseug - a WSGI (Web Server Gateway Interface) utility library for interface between web servers and web applications for the Python programming language.
* Jinja2 - an html template engine

## Contents

* [Flask Methods](#flask-methods)
    * [App Attributes & Methods](#app-attributes-methods)
    * [Request Methods](#request-methods)
    * [Render Methods](#render-methods)
    * [Decorators](#decorators)
* [URLs Quick and Dirty](#urls-quick-and-dirty)
* [Jinja Template Syntax](#jinja-template-syntax)
* [Databases in Flask](#databases-in-flask)

## Flask Methods

* `abort(<code>)`: Send error `code` to client.
* `redirect(<url>)`: Redirects `@app.route(<route>)` to redirect <url>. The `code` argument allows specification of redirect code, e.g., `..., code=301)` indicates the redirect is *permanent* as opposed to a temporary resource absence. `code` defaults to `302` (i.e., temporary redirect).

### App Attributes & Methods

App objects are created for each Flask app with `App = Flask(__name__)`. 

* `run(<host>,<port>)`: Start the Flask app server from `<host>` through `<port>`. Until the process is ended, the Flask app will wait for calls from clients. This is not a robust web server, it is for **testing only**

### Request Methods

* `request.args`: the key/value pairs in the URL query string
* `request.form`: the key/value pairs in the body, from a HTML post form, or JavaScript request that isn't JSON encoded
* `request.files`: the files in the body, which Flask keeps separate from form. HTML forms must use `enctype=multipart/form-data` or files will not be uploaded.
* `request.remote_addr`: return the IP address of the client
* `request.values`: combined args and form, preferring args if keys overlap

### Render Methods

* `render_template('path/under/template/file.html', [arg_1 = <val1>, ...])`: Render `.html` file inside the `template` directory (default directory name may be changed). Allows `arg_.` to be used in Jinja `{{ arg_. }}` variables. For example: 

```python
@app.route('/authors/<authors_last_name>')
def author(authors_last_name): #passed from the url above
return render_template('author.html',
                   author_ln='Frank Herbert') #Used in {{ author_ln }} in HTML
```

**Note:** Flask automatically looks for templates in a `templates/` directory relative to your app file. You don't need to specify `templates/` in the path. To customize this location, use `app = Flask(__name__, template_folder='custom_folder')`.

* `render_template_string(<html_str>, [arg_1 = <val1>, ...])`: Render HTML code with the ability to insert argument values into the string without Python string manipulation. For example:

### Decorators

* `@app.errorhandler(<code>)`: Specifies the following method for the event when the server sends error `code` to the client. This allows override of default Flask error templates. For example, 
    ```python
    @app.errorhandler(<code>)
    def not_found(error):
        return render_template('404.html'), 404
    ```
Note that by default, flask methods return a `200` code, (i.e., 'okay'). To specify otherwise, return the correct code as the second element of a tuple (e.g., as above).
* **Route Decorator**: `@app.route('/route/to/site')` Specifies the directory `/route/to/site`, which will run the following (single) function/method when accessed by a client.
```python
@app.route('/')
def hello_world():
    db_connection = connect_db()  # helper function
    data = process_data()          # another helper function
    return render_template('index.html', data=data)
```
Multiple routes can use the same function:
```python
@app.route('/')
@app.route('/home')
def index():
    return "Home page"
```
* **Dynamic Routes**: Generated with `<` and `>`. For example
```python
@app.route('/authors/<authors_last_name>')
def author(authors_last_name): #passed from the url above
    return render_template('author.html',
                        author_ln=authors_last_name)
```
This will fill in the `{{ author_ln }}` Jinja variable in the `.html` file with the author's last name.
* **Data Types**: Dynamic route values' data types may be specified preceding the value name. E.g., `@app.route('/people/<int:age>')`.

## URLs Quick and Dirty

![URL Breakdown](images/url-breakdown.jpg)

4 parts:

* **Protocol:** specifies how the web server should interpret the information you are sending it.
* **Host:** points to the domain name of the web server you want to communicate with. Each host is associated with a specific IP address.
* **Port:** Hold additional information used to connect with the host (think apartment number to the host's street address)
* **Path:** Indicates where on the server the file you are requesting lives.

## Jinja Template Syntax

Other template styles may be specified, but Jinja is the default style.

* **Variables - `{{ <var> }}`**: A placeholder for template building
* **For-Loop**: Render HTML with a for-loop iteration over an input variable defined within the `app()`. `authors
```html
<ul>
    {% for author in authors %}
        <li>{{ author }}</li>
    {% endfor %}
</ul>
```
* **If-Else Conditionals**: Renders HTML based on a conditional switch. Conditionals come between `%`s and are finished with `endif`. The following adds bold (`<b>` tag) to `'name'` of `author` if it has `country_id == 2`.
```html
<ul>
    {% if author['country_id']== 2 %}
        <li>{{author['id']}}: {{author['name']}}</li>
    {% else %}
        <li><b>{{author['id']}}: {{author['name']}}</b></li>
    {% endif %}
</ul>
```
* **Joins

## Databases in Flask

`sqlite3` has a built-in module for python, making it convenient for managing SQL databases in python. A `sqlite3` database may be accessed with the following flask method:

```python
import sqlite3

def connect_db():
    return sqlite3.connect(config.DATABASE_NAME)
```

A simple query method for this database might look like the following:

```python
@app.route('/')
def hello_world():
    db_connetion = connect_db()
    cursor = db_connection.execute('SELECT id, name FROM author;')
    authors = [dict(id=row[0], name=row[1]) for row in cursor.fetchall()]
    return render_template('database/authors.html', authors = authors)
```

## File Input in Flask

*"never trust user input"*

* [Guide Here](http://flask.pocoo.org/docs/0.12/patterns/fileuploads/)

## References

* [Flask Tutorial Step by Step - Udemy Course](https://www.udemy.com/course/draft/1114060)