from flask import Flask, request, redirect, render_template
import pymysql

app = Flask(__name__)

# Database bağlantısı
def get_db():
    return pymysql.connect(
        host='192.168.1.165',   # DB veya HAProxy IP
        port=3306,
        user='root',
        password='ildeniz',
        database='flowboard',
        charset='utf8mb4'
    )

@app.route('/')
def home():
    return '''
    <h1>Merhaba Flask + MariaDB!</h1>
    <p><a href="/register">Yeni Kullanıcı Kaydet</a></p>
    <p><a href="/users">Kullanıcıları Göster</a></p>
    '''

# Register formu
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        mail = request.form['mail']

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, surname, mail) VALUES (%s, %s, %s)",
                (name, surname, mail)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/users')
        except Exception as e:
            return f"Kayıt hatası: {str(e)}<br><a href='/'>Ana sayfaya dön</a>"

    return render_template("register.html")

# Kullanıcıları listeleme
@app.route('/users')
def users():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, surname, mail FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()

        return render_template("users.html", users=users)
    except Exception as e:
        return f'Database hatası: {str(e)}<br><a href="/">← Ana sayfaya dön</a>'

if __name__ == '__main__':
    app.run(debug=True)
