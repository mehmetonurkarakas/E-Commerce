import datetime
from flask import Flask, render_template, request, redirect, url_for
from init_db import create_table, insert_book, get_all_books
from login import Login

app = Flask(__name__)
create_table()
login = Login(app)


@app.route('/')
def index():
    books = get_all_books()
    return render_template('index.html', books=books)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        pages_num = int(request.form['pages_num'])
        review = request.form['review']

        insert_book(title, author, pages_num, review)
        return redirect(url_for('index'))

    return render_template('create.html')
