from flask import Flask, render_template, request, redirect, session, abort
import sqlite3
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
DATABASE = 'finance.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_number TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            paid INTEGER DEFAULT 0,
            error INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Login failed"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return  redirect("/.login")

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":
        t_type = request.form["type"]
        name = request.form["name"]
        amount = float(request.form["amount"])
        transaction_number = request.form["transaction_number"]
        transaction_date = request.form["due_date"]
        due_date = request.form["due_date"]
        c.execute(
            "INSERT INTO transactions (type, name, amount, due_date, transaction_number, transaction_date) VALUES (?, ?, ?, ?, ?, ?)",
            (t_type, name, amount, due_date, transaction_number, transaction_date))
        conn.commit()
        return redirect("/")

    # FETCH DATA AFTER redirect, not before INSERT
    c.execute("SELECT * FROM transactions WHERE type='credit' AND error = 0")
    credit = [dict(id=row[0], type=row[1], name=row[2], amount=row[3], due_date=row[4],
                   transaction_date=row[5], transaction_number=row[6],
                   paid=bool(row[7]), error=bool(row[8])) for row in c.fetchall()]

    c.execute("SELECT * FROM transactions WHERE type='debit' AND error = 0")
    debit = [dict(id=row[0], type=row[1], name=row[2], amount=row[3], due_date=row[4],
                  transaction_date=row[5], transaction_number=row[6],
                  paid=bool(row[7]), error=bool(row[8])) for row in c.fetchall()]

    conn.close()
    return render_template("index.html", credit=credit, debit=debit)

@app.route("/mark_paid/<int:transaction_id>")
def mark_paid(transaction_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE transactions SET paid = 1 WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/mark_error/<int:transaction_id>")
def mark_error(transaction_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE transactions SET error = 1 WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=10000)

