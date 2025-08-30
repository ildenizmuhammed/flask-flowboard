from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Veritabanını oluştur
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# Ana sayfa (register formu)
@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Veritabanına kaydet
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

        return redirect("/users")  # Kayıttan sonra kullanıcıları göster

    return render_template("register.html")

# Kayıtlı kullanıcıları listele
@app.route("/users")
def users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("users.html", users=users)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
