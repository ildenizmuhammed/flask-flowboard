from flask import Flask

app = Flask(__name__)

@app.route('/')
def merhaba_flask():
    return '''
    <html>
        <head>
            <title>İlk Flask Uygulamam</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>🎉 Merhaba Flask!</h1>
            <h2>🎉 Bugün Nasılsın?</h2>
            <p>İlk Flask uygulamam başarıyla çalışıyor!</p>
            <p>Sunucu: Debian 12 + Apache</p>
            <p><a href="/index2">Çıkmak için tıklayın.</a></p>
        </body>
    </html>
    '''

@app.route('/index2')
def index2():
    return '''
    <html>
        <head>
            <title>Index2</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>🎉 Güle Güle Flask!</h1>
            <h2>🎉 Görüşmek üzere</h2>
            <p>İkinci Flask sayfası başarıyla çalışıyor!</p>
            <p>Sunucu: Debian 12 + Apache</p>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
