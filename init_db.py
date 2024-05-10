import psycopg2


def connect_db():
    conn = psycopg2.connect(
        database="studentapp", user='onur', password='123', host='127.0.0.1', port='5432'
    )
    return conn


def create_table():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS books;')
    cur.execute('CREATE TABLE books (id serial PRIMARY KEY,'
                'title varchar (150) NOT NULL,'
                'author varchar (50) NOT NULL,'
                'pages_num integer NOT NULL,'
                'review text,'
                'date_added date DEFAULT CURRENT_TIMESTAMP);'
                )

    cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    student_id INT NOT NULL,
                    name VARCHAR(25) NOT NULL,
                    surname VARCHAR(25) NOT NULL,
                    username VARCHAR(25) NOT NULL,
                    password VARCHAR(16) NOT NULL,
                    email VARCHAR(100),
                    reputation INT,
                    CONSTRAINT email_check CHECK (email LIKE '%@%.%')
                )
            """)
    cur.execute("TRUNCATE TABLE users RESTART IDENTITY CASCADE")

    cur.execute("""
                INSERT INTO users (student_id, name, surname, username, password, email, reputation)
                VALUES 
                    (123456, 'onur', 'Doe', 'onur', '123', 'johndoe@example.com', 100),
                    (654321, 'emre', 'Smith', 'emre', '123', 'janesmith@example.com', 80)
            """)

    cur.execute('INSERT INTO books (title, author, pages_num, review)'
                'VALUES (%s, %s, %s, %s)',
                ('A Tale of Two Cities',
                 'Charles Dickens',
                 489,
                 'A great classic!')
                )

    cur.execute('INSERT INTO books (title, author, pages_num, review)'
                'VALUES (%s, %s, %s, %s)',
                ('Anna Karenina',
                 'Leo Tolstoy',
                 864,
                 'Another great classic!')
                )

    conn.commit()
    conn.close()


def insert_book(title, author, pages_num, review):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO books (title, author, pages_num, review)'
                'VALUES (%s, %s, %s, %s)',
                (title, author, pages_num, review))
    conn.commit()
    conn.close()


def get_all_books():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM books;')
    books = cur.fetchall()
    conn.close()
    return books
