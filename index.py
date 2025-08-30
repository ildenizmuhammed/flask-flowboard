from flask import Flask, request, redirect, render_template, flash, url_for
import pymysql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # For flash messages

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

# Initialize database tables
def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Create blog_posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author VARCHAR(100) NOT NULL,
                category VARCHAR(50) DEFAULT 'Genel',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                image_url VARCHAR(255),
                excerpt TEXT
            )
        """)
        
        # Create categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            )
        """)
        
        # Insert default categories
        cursor.execute("""
            INSERT IGNORE INTO categories (name, description) VALUES 
            ('Teknoloji', 'Teknoloji ile ilgili yazılar'),
            ('Yaşam', 'Günlük yaşam ve kişisel deneyimler'),
            ('Bilim', 'Bilimsel konular ve araştırmalar'),
            ('Sanat', 'Sanat ve kültür yazıları'),
            ('Genel', 'Genel konular')
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def home():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get recent posts
        cursor.execute("""
            SELECT id, title, excerpt, author, category, created_at, image_url 
            FROM blog_posts 
            ORDER BY created_at DESC 
            LIMIT 6
        """)
        recent_posts = cursor.fetchall()
        
        # Get categories
        cursor.execute("SELECT name, COUNT(*) as post_count FROM categories c LEFT JOIN blog_posts p ON c.name = p.category GROUP BY c.name")
        categories = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("index.html", recent_posts=recent_posts, categories=categories)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/blog')
def blog():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        page = request.args.get('page', 1, type=int)
        per_page = 5
        offset = (page - 1) * per_page
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM blog_posts")
        total_posts = cursor.fetchone()[0]
        
        # Get posts with pagination
        cursor.execute("""
            SELECT id, title, excerpt, author, category, created_at, image_url 
            FROM blog_posts 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (per_page, offset))
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        total_pages = (total_posts + per_page - 1) // per_page
        
        return render_template("blog.html", posts=posts, page=page, total_pages=total_pages)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, author, category, created_at, image_url 
            FROM blog_posts 
            WHERE id = %s
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            return "Post bulunamadı", 404
        
        cursor.close()
        conn.close()
        
        return render_template("post_detail.html", post=post)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/category/<category_name>')
def category_posts(category_name):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, excerpt, author, category, created_at, image_url 
            FROM blog_posts 
            WHERE category = %s 
            ORDER BY created_at DESC
        """, (category_name,))
        posts = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template("category.html", posts=posts, category=category_name)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/new-post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        author = request.form['author']
        category = request.form['category']
        excerpt = request.form['excerpt']
        image_url = request.form['image_url']

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO blog_posts (title, content, author, category, excerpt, image_url) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, content, author, category, excerpt, image_url))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Blog yazısı başarıyla eklendi!', 'success')
            return redirect('/blog')
        except Exception as e:
            flash(f'Yazı ekleme hatası: {str(e)}', 'error')
            return redirect('/new-post')

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return render_template("new_post.html", categories=categories)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

# Initialize database when app starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)
