from flask import Flask, render_template

app = Flask(__name__)

# Örnek ürün verileri (sonradan veritabanına bağlanabilir)
products = [
    {
        "name": "Derin Siyah Kolye",
        "description": "Tarzınızı ön plana çıkaracak şık siyah kolye.",
        "price": "₺149",
        "image": "https://images.unsplash.com/photo-1616627988683-1c75663ed38b?auto=format&fit=crop&w=500&q=60"
    },
    {
        "name": "Altın Rengi Bileklik",
        "description": "Günlük ve özel kombinler için mükemmel bileklik.",
        "price": "₺99",
        "image": "https://images.unsplash.com/photo-1580910051075-80b66bbd88ef?auto=format&fit=crop&w=500&q=60"
    },
    {
        "name": "Minimalist Saat",
        "description": "Şıklığın ve sadeliğin birleştiği tasarım.",
        "price": "₺249",
        "image": "https://images.unsplash.com/photo-1599945939312-0a5d51c0172c?auto=format&fit=crop&w=500&q=60"
    },
    {
        "name": "Klasik Yüzük Seti",
        "description": "Her kombinle uyum sağlayacak şık yüzük seti.",
        "price": "₺129",
        "image": "https://images.unsplash.com/photo-1599945939312-0a5d51c0172c?auto=format&fit=crop&w=500&q=60"
    }
]

@app.route('/')
def index():
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
