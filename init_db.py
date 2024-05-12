import psycopg2


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
    cur.execute("""drop table if exists items""")
    cur.execute("""
                    CREATE TABLE items (
                    id serial PRIMARY KEY,
                    name VARCHAR ( 100 ) NOT NULL,
                    price FLOAT NOT NULL
                    );
                    """)

    cur.execute("""insert into items (name, price) values ('item1', 10)""")
    cur.execute("""insert into items (name, price) values ('item2', 20)""")
    cur.execute("""insert into items (name, price) values ('item3', 30)""")
    cur.execute("""insert into items (name, price) values ('item4', 40)""")
    
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
    print(items)
    return items
