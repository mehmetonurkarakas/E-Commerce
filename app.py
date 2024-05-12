from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db
from login import logout, register, login,get_all_items
from navbar import dashboard, feedbacks, products, orders

app = Flask(__name__)
app.secret_key = 'onur'
conn = connect_db()
create_table()

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', 'dashboard',dashboard , methods=['GET', 'POST'])
app.add_url_rule('/feedbacks', 'feedbacks', feedbacks, methods=['GET', 'POST'])
app.add_url_rule('/products', 'products', products, methods=['GET', 'POST'])
app.add_url_rule('/orders', 'orders', orders, methods=['GET', 'POST'])



@app.route('/')
def home():
    # if 'loggedin' in session:
    #     return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/house')
def house():
    if 'loggedin' in session:
        items = get_all_items()
        print("--", items)
        return render_template('home.html', username=session['username'], items=items)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)