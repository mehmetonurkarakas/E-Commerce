from flask import session, redirect, url_for
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, get_all_items


def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


def feedbacks():
    if 'loggedin' in session:
        return render_template('feedbacks.html')
    return redirect(url_for('login'))


def products():
    if 'loggedin' in session:
        return render_template('products.html')
    return redirect(url_for('login'))

def orders():
    if 'loggedin' in session:
        return render_template('orders.html')
    return redirect(url_for('login'))
