import sqlite3
from werkzeug.security import generate_password_hash
from app import DATABASE

email = "khoshanon@yahoo.com"
plain_password = "testFinanceProject123!"

hashed_password = generate_password_hash(plain_password)

conn = sqlite3.connect(DATABASE)
c = conn.cursor()
c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
conn.commit()
conn.close()

print(f"User {email} added successfully.")
