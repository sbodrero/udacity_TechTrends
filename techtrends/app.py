import sqlite3
import logging
import sys
import datetime

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to print stdout
def log_to_stdout(message):
    # Here a is the array holding the objects
    # passed as the argument of the function
    sys.stdout.write(message)

# Function to print stderr
def log_to_stderr(message):
    # Here a is the array holding the objects
    # passed as the argument of the function
    sys.stderr.write(message)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post


# Function to get posts count
def get_post_count():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    return post_count


# Function to get database access counter
def get_db_access_count():
    connection = get_db_connection()
    count = connection.execute('SELECT counter FROM metrics WHERE name="db_access_count"').fetchone()
    connection.close()
    return count[0]

# Function to increment database access counter
def increment_by_one_db_access_count():
    connection = get_db_connection()
    connection.execute('UPDATE metrics set counter = counter+1 WHERE name="db_access_count"')
    connection.commit()
    connection.close()

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Define the main route of the web application
@app.route('/')
def index():
    increment_by_one_db_access_count()
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define the healthz endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result": "OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response


# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    post_count = get_post_count()
    db_access_count = get_db_access_count()
    response = app.response_class(
            response=json.dumps({"data": {"db_connection_count": db_access_count,
                                          "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )

    return response


# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    increment_by_one_db_access_count()
    post = get_post(post_id)
    if post is None:
        log_to_stderr('Non existing article with id. ' + str(post_id))
        return render_template('404.html'), 404
    else:
        log_to_stdout('Article "' + post['title'] + '" retrieved ')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    increment_by_one_db_access_count()
    log_to_stdout('About Us page visited')
    return render_template('about.html')


# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            log_to_stdout('New Article "' + title + '" recorded ')

            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":

    logging.basicConfig(filename='app.log', level=logging.DEBUG)

    app.run(host='0.0.0.0', port='3111')
