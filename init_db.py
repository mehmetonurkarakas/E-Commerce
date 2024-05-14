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

    # cur.execute("""
    #             CREATE TABLE IF NOT EXISTS users (
    #                 user_id SERIAL PRIMARY KEY,
    #                 student_id INT NOT NULL,
    #                 name VARCHAR(25) NOT NULL,
    #                 surname VARCHAR(25) NOT NULL,
    #                 username VARCHAR(25) NOT NULL,
    #                 password VARCHAR(16) NOT NULL,
    #                 email VARCHAR(100),
    #                 reputation INT,
    #                 CONSTRAINT email_check CHECK (email LIKE '%@%.%')
    #             )
    #         """)
    # cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")
    #
    # cur.execute("""
    #             INSERT INTO users (student_id, name, surname, username, password, email, reputation)
    #             VALUES
    #                 (123456, 'onur', 'Doe', 'onur', '123', 'johndoe@example.com', 100),
    #                 (654321, 'emre', 'Smith', 'emre', '123', 'janesmith@example.com', 80)
    #         """)

    conn.commit()
    conn.close()


def get_all_items():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * from items;')
    items = cur.fetchall()
    conn.close()
    return items


def specific_items(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM items WHERE user_id = %s ORDER BY item_id;', [user_id])
    items = cur.fetchall()
    conn.close()
    return items



