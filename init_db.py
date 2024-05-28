from datetime import timedelta
from decimal import Decimal

import psycopg2
from werkzeug.security import generate_password_hash


def connect_db():
    conn = psycopg2.connect(
        database="studentapp", user='onur', password='123', host='127.0.0.1', port='5432'
    )

    return conn


def create_table():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""drop table if exists users""")
    cur.execute("""
                    CREATE TABLE users (
                    id serial PRIMARY KEY,
                    fullname VARCHAR ( 100 ) NOT NULL,
                    username VARCHAR ( 50 ) NOT NULL,
                    password VARCHAR ( 255 ) NOT NULL,
                    email VARCHAR ( 50 ) NOT NULL
                    );
                    """)

    _hashed_password = generate_password_hash('123')

    cur.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                ('onure', 'onur', _hashed_password, 'a@gmail.com'))
    cur.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                ('emre', 'emre', _hashed_password, 'b@gmail.com'))

    cur.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                ('ali', 'ali', _hashed_password, 'c@gmail.com'))
    conn.commit()

    cur.execute("""drop table if exists items""")
    cur.execute("""
                    CREATE TABLE items (
                    item_id serial PRIMARY KEY,
                    name VARCHAR ( 100 ) NOT NULL,
                    price FLOAT NOT NULL,
                    user_id INT REFERENCES users(id)
                    );
                    """)

    cur.execute("""insert into items (name, price,user_id) values ('item1', 10,1)""")
    cur.execute("""insert into items (name, price,user_id) values ('item2', 20,1)""")
    cur.execute("""insert into items (name, price,user_id) values ('item3', 30,2)""")
    cur.execute("""insert into items (name, price,user_id) values ('item4', 40,2)""")
    conn.commit()
    conn.close()


def create_bid_table():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""drop table if exists bids""")
    cur.execute("""
                    CREATE TABLE bids (
                    bid_id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    item_id INT NOT NULL,
                    bid_amount FLOAT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id)
                    );""")
    conn.commit()
    conn.close()


def format_timedelta(td):
    # Zamanı saat, dakika, saniye formatına dönüştürmek için bir fonksiyon
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{td.days} days, {hours} hours, {minutes} minutes, {seconds} seconds"



def get_all_items():
    conn = None
    try:
        conn = connect_db()
        with conn.cursor() as cur:
            cur.execute('''
                SELECT
                    item_id,
                    name,
                    price,
                    user_id,
                    created_at,
                    expires_at,
                    CASE
                        WHEN expires_at IS NOT NULL AND expires_at > CURRENT_TIMESTAMP
                            THEN EXTRACT(EPOCH FROM (expires_at - CURRENT_TIMESTAMP))
                        ELSE
                            0
                    END AS leftTime
                FROM
                    items
                WHERE
                    isActive = TRUE
                ORDER BY
                    item_id;
            ''')
            items = cur.fetchall()
            items_list = []
            for item in items:
                item_list = list(item)  # tuple'ı listeye dönüştür
                if isinstance(item_list[6], Decimal):
                    item_list[6] = int(item_list[6])  # Convert Decimal to int
                if item_list[6] != 0:
                    item_list[6] = timedelta(seconds=item_list[6])
                else:
                    item_list[6] = timedelta(seconds=0)
                items_list.append(item_list)
            return items_list
    except psycopg2.DatabaseError as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()




def specific_items(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items WHERE user_id = %s ORDER BY item_id;', [user_id])
    items = cur.fetchall()
    conn.close()
    return items


def create_admin():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""drop table if exists admins""")
    cur.execute("""
                    CREATE TABLE admins (
                    id serial PRIMARY KEY,
                    fullname VARCHAR ( 100 ) NOT NULL,
                    username VARCHAR ( 50 ) NOT NULL,
                    password VARCHAR ( 255 ) NOT NULL,
                    email VARCHAR ( 50 ) NOT NULL
                    );
                    """)
    _hashed_password = generate_password_hash('123')
    cur.execute("INSERT INTO admins (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                ('admin', 'admin', _hashed_password, 'admin@gmail.com'))

    conn.commit()




