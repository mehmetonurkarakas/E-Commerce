from flask import session, redirect, url_for
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, get_all_items

conn = connect_db()


def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print("password:", password)

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))

        account = cursor.fetchone()
        print("account :", account)

        if account:
            password_rs = account['password']
            print("from database password:", password_rs)
            print(password)
            if check_password_hash(password_rs, password):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                return redirect(url_for('house'))
            else:
                flash('Incorrect username/password')
        else:
            flash('Incorrect username/password')

    return render_template('login.html')


def register():
    print("register function")
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if (request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email'
            in request.form):
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                           (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html')


def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)

    return redirect(url_for('login'))