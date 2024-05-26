from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, create_admin, create_bid_table
from login import logout, register, login, get_all_items
from navbar import dashboard, feedbacks, products, orders
from productOperation import create_item_route, update_item_route, delete_item_route
from bid import place_bid, bid_success
from admin import admin_users, admin_update_user, admin_delete_user, is_admin

app = Flask(__name__)
app.secret_key = 'onur'
conn = connect_db()
#create_bid_table()
#create_table()
#create_admin()

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', 'dashboard', dashboard, methods=['GET', 'POST'])
app.add_url_rule('/feedbacks', 'feedbacks', feedbacks, methods=['GET', 'POST'])
app.add_url_rule('/products', 'products', products, methods=['GET', 'POST'])
app.add_url_rule('/orders', 'orders', orders, methods=['GET', 'POST'])
app.add_url_rule('/create_item_route', 'create_item_route', create_item_route, methods=['POST'])
app.add_url_rule('/update_item/<int:item_id>', 'update_item_route', update_item_route, methods=['POST'])
app.add_url_rule('/delete_item/<int:item_id>', 'delete_item_route', delete_item_route, methods=['POST', 'DELETE'])
app.add_url_rule('/place_bid/<int:item_id>', 'place_bid', place_bid, methods=['GET', 'POST'])
app.add_url_rule('/bid_success/<int:item_id>', 'bid_success', bid_success)
app.add_url_rule('/admin/users', 'admin_users', admin_users)
app.add_url_rule('/admin/update_user/<int:user_id>', 'admin_update_user', admin_update_user, methods=['POST'])
app.add_url_rule('/admin/delete_user/<int:user_id>', 'admin_delete_user', admin_delete_user, methods=['POST'])


@app.route('/')
def home():
    # if 'loggedin' in session:
    #     return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/reports')
def reports():
    if 'loggedin' in session and session.get('is_admin'):
        reports_data = []
        return render_template('reports.html', reports=reports_data)
    return redirect(url_for('login'))


@app.route('/house')
def house():
    if 'loggedin' in session:
        items = get_all_items()
        return render_template('home.html', username=session['username'], items=items, is_admin=is_admin())
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if 'loggedin' in session:
        if session.get('is_admin'):
            cursor.execute('SELECT * FROM admins WHERE id = %s', [session['id']])
        else:
            cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])

        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'loggedin' in session:
        fullname = request.form['fullname']
        username = request.form['username']
        email = request.form['email']

        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        cursor.execute('SELECT * FROM users WHERE username = %s AND id != %s', (username, session['id']))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username is already in use. Please choose a different one.")
            return redirect(url_for('profile'))

        cursor.execute('UPDATE users SET fullname = %s, username = %s, email = %s WHERE id = %s',
                       (fullname, username, email, session['id']))
        conn.commit()

        flash("Profile updated successfully.")
        return redirect(url_for('profile'))
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
