from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash
from init_db import create_table, connect_db, create_admin,create_bid_table
from login import logout, register, login, get_all_items
from navbar import dashboard, feedbacks, products, orders
from productOperation import create_item_route, update_item_route, delete_item_route

app = Flask(__name__)
app.secret_key = 'onur'
conn = connect_db()
create_bid_table()
# create_table()
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


@app.route('/')
def home():
    # if 'loggedin' in session:
    #     return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))


@app.route('/place_bid/<int:item_id>', methods=['GET', 'POST'])
def place_bid(item_id):
    if 'loggedin' in session:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if request.method == 'POST':
            user_id = session['id']
            bid_amount = float(request.form['bid_amount'])

            # Get the current price of the item
            cursor.execute('SELECT price FROM items WHERE item_id = %s', (item_id,))
            current_price = cursor.fetchone()[0]

            # Get the highest bid for the item
            cursor.execute('SELECT MAX(bid_amount) FROM bids WHERE item_id = %s', (item_id,))
            highest_bid = cursor.fetchone()[0]

            if highest_bid is None:
                highest_bid = 0

            # Ensure the bid is higher than both the initial price and the highest bid
            if bid_amount > current_price and bid_amount > highest_bid:
                cursor.execute('INSERT INTO bids (user_id, item_id, bid_amount) VALUES (%s, %s, %s)',
                               (user_id, item_id, bid_amount))
                conn.commit()

                # Update item price in items table
                cursor.execute('UPDATE items SET price = %s WHERE item_id = %s', (bid_amount, item_id))
                conn.commit()

                return redirect(url_for('bid_success', item_id=item_id))  # Pass item_id to bid_success
            else:
                flash('Your bid must be higher than the current price and the highest bid.')

        # Fetch the item details for displaying
        cursor.execute('SELECT * FROM items WHERE item_id = %s', (item_id,))
        item = cursor.fetchone()

        return render_template('place_bid.html', item=item)
    return redirect(url_for('login'))


@app.route('/bid_success/<int:item_id>')
def bid_success(item_id):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM items WHERE item_id = %s', (item_id,))
    item = cursor.fetchone()
    return render_template('bid_success.html', item=item)



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


def is_admin():
    return 'loggedin' in session and session.get('is_admin', False)


@app.route('/admin/users')
def admin_users():
    if is_admin():
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM users order by id;')
        all_users = cursor.fetchall()
        return render_template('users.html', users=all_users)
    else:
        return redirect(url_for('home'))


@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
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


@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
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


if __name__ == "__main__":
    app.run(debug=True)
