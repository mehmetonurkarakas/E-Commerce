from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, create_admin
from login import logout, register, login, get_all_items
from navbar import dashboard, feedbacks, products, orders
conn = connect_db()


def place_bid(item_id):
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            user_id = session['user_id']
            bid_amount = float(request.form['bid_amount'])

            # Get the current price of the item
            cursor.execute('SELECT current_price FROM items WHERE item_id = %s', (item_id,))
            current_price_row = cursor.fetchone()
            current_price = float(current_price_row[0]) if current_price_row[0] is not None else 0

            # Get the highest bid for the item
            cursor.execute('SELECT MAX(bid_amount) FROM bids WHERE item_id = %s', (item_id,))
            highest_bid_row = cursor.fetchone()
            highest_bid = float(highest_bid_row[0]) if highest_bid_row[0] is not None else 0


            # Ensure the bid is higher than both the initial price and the highest bid
            if bid_amount > current_price and bid_amount > highest_bid:
                cursor.execute('INSERT INTO bids (user_id, item_id, bid_amount) VALUES (%s, %s, %s)',
                               (user_id, item_id, bid_amount))
                conn.commit()

                # Update item price in items table
                cursor.execute('UPDATE items SET current_price = %s WHERE item_id = %s', (bid_amount, item_id))
                conn.commit()

                return redirect(url_for('bid_success', item_id=item_id))  # Pass item_id to bid_success
            else:
                flash('Your bid must be higher than the current price and the highest bid.')

        # Fetch the item details for displaying
        cursor.execute('SELECT * FROM items WHERE item_id = %s', (item_id,))
        item = cursor.fetchone()

        return render_template('place_bid.html', item=item)
    return redirect(url_for('login'))


def bid_success(item_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM items WHERE item_id = %s', (item_id,))
    item = cursor.fetchone()
    return render_template('bid_success.html', item=item)

