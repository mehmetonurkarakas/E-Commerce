import os

from flask import Flask, request, session, redirect, url_for, render_template, flash, jsonify
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from init_db import create_table, connect_db, create_admin
from login import logout, register, login, get_all_items
from navbar import dashboard, feedbacks, products, orders
from datetime import datetime
from db_operations import create_item, update_item, delete_item, get_all_categories, get_all_conditions
from bid import place_bid, bid_success
from admin import admin_users, admin_update_user, admin_delete_user, is_admin

app = Flask(__name__)
app.secret_key = 'onur'
conn = connect_db()
# create_table()
# create_admin()

app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout)
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/dashboard', 'dashboard', dashboard, methods=['GET', 'POST'])
app.add_url_rule('/feedbacks', 'feedbacks', feedbacks, methods=['GET', 'POST'])
app.add_url_rule('/products', 'products', products, methods=['GET', 'POST'])
app.add_url_rule('/orders', 'orders', orders, methods=['GET', 'POST'])
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
            cursor.execute('SELECT * FROM admins WHERE id = %s', [session['user_id']])
        else:
            cursor.execute('SELECT * FROM users WHERE user_id = %s', [session['user_id']])

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

        cursor.execute('SELECT * FROM users WHERE username = %s AND user_id != %s', (username, session['user_id']))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username is already in use. Please choose a different one.")
            return redirect(url_for('profile'))

        cursor.execute('UPDATE users SET fullname = %s, username = %s, email = %s WHERE user_id = %s',
                       (fullname, username, email, session['user_id']))
        conn.commit()

        flash("Profile updated successfully.")
        return redirect(url_for('profile'))
    return redirect(url_for('login'))



@app.route('/create_item', methods=['POST'])
def create_item_route():
    if 'loggedin' in session:
        user_id = session['user_id']
        title = request.form['title']
        starting_price = request.form['starting_price']
        category_id = request.form['category_id']
        condition_id = request.form['condition_id']
        description = request.form['description']
        stock = request.form['stock']

        # Validate the form fields
        if not title or not starting_price or not category_id or not condition_id or not stock or not description:
            flash("Please fill out all fields.")
            return redirect(url_for('products'))

        with conn.cursor() as cur:
            try:
                create_item(cur, user_id, category_id, condition_id, title,description, starting_price,stock)
                conn.commit()
                flash("Item created successfully.")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}")

        return redirect(url_for('products'))
    return redirect(url_for('login'))


@app.route('/update_item/<int:item_id>', methods=['POST'])
def update_item_route(item_id):
    if 'loggedin' in session:
        title = request.form['title']
        starting_price = request.form['starting_price']

        with conn.cursor() as cur:
            try:
                update_item(cur, item_id, title, starting_price)
                conn.commit()
                flash("Item updated successfully.")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}")

        return redirect(url_for('products'))
    return redirect(url_for('login'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item_route(item_id):
    if 'loggedin' in session:
        with conn.cursor() as cur:
            try:
                delete_item(cur, item_id)
                conn.commit()
                flash("Item deleted successfully.")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {str(e)}")

        return redirect(url_for('products'))
    return redirect(url_for('login'))

app.add_url_rule('/create_item', 'create_item_route', create_item_route, methods=['POST'])
app.add_url_rule('/update_item/<int:item_id>', 'update_item_route', update_item_route, methods=['POST'])
app.add_url_rule('/delete_item/<int:item_id>', 'delete_item_route', delete_item_route, methods=['DELETE'])



if __name__ == "__main__":
    app.run(debug=True)
