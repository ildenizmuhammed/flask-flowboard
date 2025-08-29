from flask import Flask
import pymysql

app = Flask(__name__)

# Database bağlantısı
def get_db():
    return pymysql.connect(
        host='192.168.1.165',     # HAProxy IP
        port=3306,
        user='root',           # Buraya kullanıcı adınızı yazın
        password='ildeniz',   # Buraya şifrenizi yazın
        database='mysql',       # Buraya database adınızı yazın
        charset='utf8mb4'
    )

@app.route('/')
def merhaba_flask():
    return '''
    <h1>Merhaba Flask!</h1>
    <p>İlk Flask uygulamam başarıyla çalışıyor!</p>
    <p>Sunucu: Debian 12 + Apache</p>
    <p><a href="/index2">Çıkmak için tıklayın.</a></p>
    <p><a href="/users">Kullanıcıları Göster</a></p>
    '''

@app.route('/index2')
def index2():
    return '''
    <h1>Güle Güle Flask!</h1>
    <p>İkinci Flask sayfası başarıyla çalışıyor!</p>
    <p>Sunucu: Debian 12 + Apache</p>
    <a href="/">← Ana sayfaya dön</a>
    '''

@app.route('/users')
def users():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")  # Tablo adınızı buraya yazın
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        html = '<h2>Kullanıcı Listesi</h2><table border="1">'
        for user in users:
            html += '<tr>'
            for field in user:
                html += f'<td>{field}</td>'
            html += '</tr>'
        html += '</table><br><a href="/">← Ana sayfaya dön</a>'
        
        return html
        
    except Exception as e:
        return f'Database hatası: {str(e)}<br><a href="/">← Ana sayfaya dön</a>'

if __name__ == '__main__':
    app.run(debug=True)