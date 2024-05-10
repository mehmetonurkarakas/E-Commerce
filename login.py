from flask import request, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2


class Login:
    def __init__(self, app):
        self.app = app
        self.app.add_url_rule('/', view_func=self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/register', view_func=self.register, methods=['GET', 'POST'])

    def connect_db(self):
        conn = psycopg2.connect(
            dbname="studentapp",
            user="onur",
            password="123",
            host="127.0.0.1",
            port="5432"
        )
        return conn

    def get_user(self, username):
        conn = self.connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        conn.close()
        return user

    def register(self):
        if request.method == 'POST':
            student_id = request.form['student_id']
            name = request.form['name']
            surname = request.form['surname']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            conn = self.connect_db()
            cur = conn.cursor()

            # Check if student_id, username, or email already exists in the database
            cur.execute("SELECT * FROM users WHERE student_id = %s OR username = %s OR email = %s",
                        (student_id, username, email))
            existing_user = cur.fetchone()

            if existing_user:
                error_message = "Student ID, username, or email is already in use. Please choose another one."
                conn.close()
                return render_template('register.html', error=error_message)
            else:
                print("else girdi")
                print(student_id, name, surname, username, password, email)
                cur.execute(
                    "INSERT INTO users (student_id, name, surname, username, password, email) VALUES (%s, %s, %s, %s, "
                    "%s, %s)",
                    (student_id, name, surname, username, password, email))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))

        return render_template('register.html')

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = self.get_user(username)

            if user and user[5] == password:
                print('User found')
                return redirect(url_for('dashboard'))
            else:
                print('User not found')
                error = 'Invalid username or password. Please try again.'
                return render_template('login.html', error=error)
        return render_template('login.html')
