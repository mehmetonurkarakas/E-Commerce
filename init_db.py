from decimal import Decimal
from datetime import datetime, timedelta

import psycopg2
from werkzeug.security import generate_password_hash
import psycopg2.extras



def connect_db():
    conn = psycopg2.connect(
        database="studentapp", user='postgres', password='Galatasaray05', host='127.0.0.1', port='5432'
    )

    return conn


def create_table():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS transactions CASCADE")
    cur.execute("DROP TABLE IF EXISTS bids CASCADE")
    cur.execute("DROP TABLE IF EXISTS notifications CASCADE")
    cur.execute("DROP TABLE IF EXISTS items CASCADE")  # Drop items before category

    # Drop category table with CASCADE to drop dependent objects (fk_category)
    cur.execute("DROP TABLE IF EXISTS category CASCADE")
    cur.execute("DROP TABLE IF EXISTS conditionofitem CASCADE")
    cur.execute("DROP TABLE IF EXISTS messages CASCADE")
    cur.execute("DROP TABLE IF EXISTS feedbacks CASCADE")
    cur.execute("DROP TABLE IF EXISTS virtualcurrency CASCADE")
    cur.execute("DROP TABLE IF EXISTS users CASCADE")

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    fullname VARCHAR(25) NOT NULL,
                    username VARCHAR(25) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100) not null,
                    reputation INT DEFAULT 0,
                    CONSTRAINT email_check CHECK (email LIKE '%@%.%')
                )
            """)
    cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")

    cur.execute("""
                CREATE TABLE virtualcurrency (
                     user_id INT NOT NULL,
                     balance NUMERIC,
                     constraint fk_user foreign key(user_id) references users(user_id),
                     constraint balance_check check(balance >= 0)
                     );
                    """)
    conn.commit()

    cur.execute("""
                CREATE TABLE feedbacks (
                     feedback_id INT PRIMARY KEY,
                     text TEXT,
                     sender_id INT,
                     receiver_id INT,
                     constraint fk_sender foreign key(sender_id) references users(user_id),
                     constraint fk_receiver foreign key(receiver_id) references users(user_id)
                    );
                    """)
    conn.commit()

    cur.execute("""
                CREATE TABLE messages (
                     message_id INT PRIMARY KEY,
                     message_text TEXT,
                     sender_id INT,
                     receiver_id INT,
                     constraint fk_sender foreign key(sender_id) references users(user_id),
                     constraint fk_receiver foreign key(receiver_id) references users(user_id)
                    );
                    """)
    conn.commit()

    # cur.execute("""drop table if exists tasks""")
    # cur.execute("""
    #             CREATE TABLE tasks (
    #                  task_id INT PRIMARY KEY,
    #                  giveaway NUMERIC,
    #                  description TEXT
    #                 );
    #                 """)
    # conn.commit()
    #
    # cur.execute("""drop table if exists taskconfig""")
    # cur.execute("""
    #             CREATE TABLE taskconfig (
    #                  user_id INT NOT NULL,
    #                  task_id INT NOT NULL,
    #                  constraint fk_user foreign key(user_id) references users(user_id),
    #                  constraint fk_task foreign key(task_id) references tasks(task_id)
    #                 );
    #                 """)
    # conn.commit()

    cur.execute("""
                CREATE TABLE category (
                     category_id INT PRIMARY KEY,
                     category_name VARCHAR(30)
                    );
                    """)
    conn.commit()

    cur.execute("""
                CREATE TABLE conditionofitem (
                     condition_id INT PRIMARY KEY,
                     condition_name VARCHAR(30)
                    );
                    """)
    conn.commit()

    cur.execute("""
                    CREATE TABLE items (
                    item_id serial PRIMARY KEY,
                    user_id INT NOT NULL,
                    category_id INT NOT NULL,
                    condition_id INT NOT NULL,
                    title VARCHAR(50),
                    description TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    starting_price NUMERIC,
                    current_price NUMERIC,
                    stock INT NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    CONSTRAINT stock_check CHECK (stock >= 0),
                    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                    CONSTRAINT fk_category FOREIGN KEY (category_id) REFERENCES category(category_id),
                    CONSTRAINT fk_condition FOREIGN KEY (condition_id) REFERENCES conditionofitem(condition_id)
                    );
                    """)

    cur.execute("""
                    CREATE TABLE notifications (
                         notification_id INT PRIMARY KEY,
                         user_id INT NOT NULL,
                         item_id INT NOT NULL,
                         constraint fk_user foreign key(user_id) references users(user_id),
                         constraint fk_item foreign key(item_id) references items(item_id)
                        );
                        """)
    conn.commit()

    cur.execute("""
                    CREATE TABLE bids (
                         bid_id SERIAL PRIMARY KEY,
                         user_id INT NOT NULL,
                         item_id INT NOT NULL,
                         bid_amount NUMERIC,
                         constraint fk_user foreign key(user_id) references users(user_id),
                         constraint fk_item foreign key(item_id) references items(item_id)
                        );
                        """)
    conn.commit()

    cur.execute("""
                    CREATE TABLE transactions (
                     transaction_id INT PRIMARY KEY,
                     buyer_id INT NOT NULL,
                     seller_id INT NOT NULL,
                     item_id INT NOT NULL,
                     price NUMERIC,
                     transaction_date DATE,
                     constraint fk_buyer foreign key(buyer_id) references users(user_id),
                     constraint fk_seller foreign key(seller_id) references users(user_id),
                     constraint fk_item foreign key(item_id) references items(item_id)
                    );
                        """)
    conn.commit()

    # cur.execute("""drop table if exists users cascade""")
    # cur.execute("""
    #                 CREATE TABLE users (
    #                 id serial PRIMARY KEY,
    #                 fullname VARCHAR ( 100 ) NOT NULL,
    #                 username VARCHAR ( 50 ) NOT NULL,
    #                 password VARCHAR ( 255 ) NOT NULL,
    #                 email VARCHAR ( 50 ) NOT NULL
    #                 );
    #                 """)

    _hashed_password = generate_password_hash('123')

    cur.execute("INSERT INTO category (category_id, category_name) VALUES (%s, %s)",(1,"Clothes"))
    cur.execute("INSERT INTO category (category_id, category_name) VALUES (%s, %s)",(2,"Tech. Device"))
    cur.execute("INSERT INTO category (category_id, category_name) VALUES (%s, %s)",(3,"Stationary"))

    cur.execute("INSERT INTO conditionofitem (condition_id, condition_name) VALUES (%s, %s)", (1, "New"))
    cur.execute("INSERT INTO conditionofitem (condition_id, condition_name) VALUES (%s, %s)", (2, "Barely used"))
    cur.execute("INSERT INTO conditionofitem (condition_id, condition_name) VALUES (%s, %s)", (3, "Old"))

    cur.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s, %s, %s, %s)",('John Doe', 'johndoe', _hashed_password, 'johndoe@example.com'))
    cur.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s, %s, %s, %s)",('Mary Doe', 'marydoe', _hashed_password, 'marydoe@example.com'))

    cur.execute("INSERT INTO items (user_id, category_id, condition_id, title, description, starting_price,start_time,end_time,stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",(1, 1, 1, 'Example Item John', 'This is an example item description.', 100,datetime.now(),datetime.now()+ timedelta(hours=1),2))
    cur.execute("INSERT INTO items (user_id, category_id, condition_id, title, description, starting_price,start_time,end_time,stock) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",(2, 1, 1, 'Example Item Mary', 'This is an example item description.', 100,datetime.now(),datetime.now()+ timedelta(hours=1),2))

    conn.commit()
    conn.close()


# def create_bid_table():
#
#     conn = connect_db()
#     cur = conn.cursor()
#
#     cur.execute("""drop table if exists bids""")
#     cur.execute("""
#                     CREATE TABLE bids (
#                     bid_id SERIAL PRIMARY KEY,
#                     user_id INT NOT NULL,
#                     item_id INT NOT NULL,
#                     bid_amount FLOAT NOT NULL,
#                     FOREIGN KEY (user_id) REFERENCES users(id),
#                     FOREIGN KEY (item_id) REFERENCES items(item_id)
#                     );""")
#     conn.commit()
#     conn.close()


def format_timedelta(td):
    # Zamanı saat, dakika, saniye formatına dönüştürmek için bir fonksiyon
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{td.days} days, {hours} hours, {minutes} minutes, {seconds} seconds"



def get_all_items():
    conn = None
    try:
        conn = connect_db()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute('''
                SELECT
                    item_id,
                    title,
                    starting_price,
                    user_id
                FROM
                    items
                ORDER BY
                    item_id;
            ''')
            items = cur.fetchall()
            return items
    except psycopg2.DatabaseError as e:
        print(f"Veritabanı hatası: {e}")
    finally:
        if conn:
            conn.close()




def specific_items(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items WHERE user_id = %s ORDER BY item_id;', (user_id,))
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




