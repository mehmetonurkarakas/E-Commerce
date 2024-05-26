import psycopg2

from init_db import connect_db
from flask import Flask, request, session, redirect, url_for, render_template, flash


def create_item_route():
    if 'loggedin' in session:
        name = request.form['name']
        price = request.form['price']
        user_id = session['id']
        create_item(name, price, user_id)
        return redirect(url_for('products'))
    return redirect(url_for('login'))


def update_item_route(item_id):
    if 'loggedin' in session:
        name = request.form['name']
        price = request.form['price']
        update_item(item_id, name, price)
        return redirect(url_for('products'))
    return redirect(url_for('login'))


def delete_item_route(item_id):
    if 'loggedin' in session:
        delete_item(item_id)
        return redirect(url_for('products'))
    return redirect(url_for('login'))


def create_item(name, price, user_id):
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute('SELECT create_item(%s, %s, %s);', (name, price, user_id))

            conn.commit()
            print("Item başarıyla eklendi.")

    except psycopg2.DatabaseError as e:
        print(f"Veritabanı hatası: {e}")

    finally:

        if conn:
            conn.close()


def update_item(item_id, name, price):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE items SET name = %s, price = %s WHERE item_id = %s;', (name, price, item_id))
    conn.commit()
    conn.close()


def delete_item(item_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM items WHERE item_id = %s;', [item_id])
    conn.commit()
    conn.close()