from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, create_admin
from login import logout, register, login, get_all_items
from navbar import dashboard, feedbacks, products, orders
conn = connect_db()


def admin_users():
    if is_admin():
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users order by id;')
        all_users = cursor.fetchall()
        return render_template('users.html', users=all_users)
    else:
        return redirect(url_for('home'))


def admin_update_user(user_id):
    if is_admin():
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            fullname = request.form['fullname']
            username = request.form['username']
            email = request.form['email']

            cursor.execute('UPDATE users SET fullname = %s, username = %s, email = %s WHERE id = %s',
                           (fullname, username, email, user_id))
            conn.commit()
            flash('User updated successfully!')
            return redirect(url_for('admin_users'))
    else:
        return redirect(url_for('house'))


def admin_delete_user(user_id):
    if is_admin():
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            cursor.execute('DELETE FROM users WHERE id = %s', [user_id])
            conn.commit()
            flash('User deleted successfully!')
            return redirect(url_for('admin_users'))
    else:
        return redirect(url_for('house'))


def is_admin():
    return 'loggedin' in session and session.get('is_admin', False)
