from flask import Flask, request, redirect, render_template, flash, url_for, session
import pymysql
from datetime import datetime
import os
from functools import wraps

app = Flask(__name__, static_folder='img', static_url_path='/img')
app.secret_key = 'your-secret-key-here'  # For flash messages and sessions

# Admin bilgileri (gerçek uygulamada veritabanında şifrelenmiş olarak saklanmalı)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

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

# Admin girişi gerekli sayfalar için decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Bu sayfaya erişmek için admin girişi yapmalısınız!', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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
        
        # Create contact_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT FALSE
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

# Admin giriş sayfası
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin girişi başarılı!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!', 'error')
    
    return render_template("admin_login.html")

# Admin çıkış
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin çıkışı yapıldı!', 'success')
    return redirect(url_for('home'))

# Admin paneli ana sayfa
@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get total posts count
        cursor.execute("SELECT COUNT(*) FROM blog_posts")
        total_posts = cursor.fetchone()[0]
        
        # Get unread messages count
        cursor.execute("SELECT COUNT(*) FROM contact_messages WHERE is_read = FALSE")
        unread_messages = cursor.fetchone()[0]
        
        # Get recent posts
        cursor.execute("""
            SELECT id, title, author, category, created_at 
            FROM blog_posts 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_posts = cursor.fetchall()
        
        # Convert timestamps to datetime objects if needed
        for i, post in enumerate(recent_posts):
            if isinstance(post[4], int):  # If created_at is timestamp
                from datetime import datetime
                recent_posts[i] = list(post)
                recent_posts[i][4] = datetime.fromtimestamp(post[4])
        
        # Get recent messages
        cursor.execute("""
            SELECT id, first_name, last_name, subject, created_at, is_read
            FROM contact_messages 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_messages = cursor.fetchall()
        
        # Convert timestamps to datetime objects if needed
        for i, message in enumerate(recent_messages):
            if isinstance(message[4], int):  # If created_at is timestamp
                from datetime import datetime
                recent_messages[i] = list(message)
                recent_messages[i][4] = datetime.fromtimestamp(message[4])
        
        cursor.close()
        conn.close()
        
        return render_template("admin_dashboard.html", 
                             total_posts=total_posts, 
                             unread_messages=unread_messages,
                             recent_posts=recent_posts,
                             recent_messages=recent_messages)
    except Exception as e:
        return f'Database hatası: {str(e)}'

# Blog yazısı ekleme (sadece admin)
@app.route('/admin/new-post', methods=['GET', 'POST'])
@admin_required
def admin_new_post():
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
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Yazı ekleme hatası: {str(e)}', 'error')
            return redirect(url_for('admin_new_post'))

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return render_template("admin_new_post.html", categories=categories)
    except Exception as e:
        return f'Database hatası: {str(e)}'

# Blog yazısı düzenleme (sadece admin)
@app.route('/admin/edit-post/<int:post_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_post(post_id):
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
                UPDATE blog_posts 
                SET title = %s, content = %s, author = %s, category = %s, excerpt = %s, image_url = %s
                WHERE id = %s
            """, (title, content, author, category, excerpt, image_url, post_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Blog yazısı başarıyla güncellendi!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Yazı güncelleme hatası: {str(e)}', 'error')
            return redirect(url_for('admin_edit_post', post_id=post_id))

    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get post data
        cursor.execute("""
            SELECT id, title, content, author, category, excerpt, image_url 
            FROM blog_posts 
            WHERE id = %s
        """, (post_id,))
        post = cursor.fetchone()
        
        if not post:
            flash('Yazı bulunamadı!', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get categories
        cursor.execute("SELECT name FROM categories")
        categories = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render_template("admin_edit_post.html", post=post, categories=categories)
    except Exception as e:
        return f'Database hatası: {str(e)}'

# Blog yazısı silme (sadece admin)
@app.route('/admin/delete-post/<int:post_id>')
@admin_required
def admin_delete_post(post_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM blog_posts WHERE id = %s", (post_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Blog yazısı başarıyla silindi!', 'success')
    except Exception as e:
        flash(f'Yazı silme hatası: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

# Blog yazısı listesi (sadece admin)
@app.route('/admin/posts')
@admin_required
def admin_posts():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, author, category, created_at 
            FROM blog_posts 
            ORDER BY created_at DESC
        """)
        posts = cursor.fetchall()
        
        # Convert timestamps to datetime objects if needed
        for i, post in enumerate(posts):
            if isinstance(post[4], int):  # If created_at is timestamp
                from datetime import datetime
                posts[i] = list(post)
                posts[i][4] = datetime.fromtimestamp(post[4])
        
        cursor.close()
        conn.close()
        
        return render_template("admin_posts.html", posts=posts)
    except Exception as e:
        return f'Database hatası: {str(e)}'

@app.route('/admin/messages')
@admin_required
def admin_messages():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name, last_name, email, subject, message, created_at, is_read
            FROM contact_messages 
            ORDER BY created_at DESC
        """)
        messages = cursor.fetchall()
        
        # Convert timestamps to datetime objects if needed
        for i, message in enumerate(messages):
            if isinstance(message[6], int):  # If created_at is timestamp
                from datetime import datetime
                messages[i] = list(message)
                messages[i][6] = datetime.fromtimestamp(message[6])
        
        cursor.close()
        conn.close()
        
        return render_template('admin_messages.html', messages=messages)
    except Exception as e:
        flash(f'Database hatası: {e}', 'error')
        return render_template('admin_messages.html', messages=[])

@app.route('/admin/mark-read/<int:message_id>')
@admin_required
def mark_message_read(message_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE contact_messages SET is_read = TRUE WHERE id = %s", (message_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        flash('Mesaj okundu olarak işaretlendi.', 'success')
    except Exception as e:
        flash(f'Hata: {e}', 'error')
    
    return redirect(url_for('admin_messages'))

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            email = request.form['email']
            subject = request.form['subject']
            message = request.form['message']
            
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO contact_messages (first_name, last_name, email, subject, message)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, email, subject, message))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            flash('Mesaj gönderilirken bir hata oluştu. Lütfen tekrar deneyin.', 'error')
            print(f"Contact form error: {e}")
    
    return render_template("contact.html")

# Initialize database when app starts
init_db()

if __name__ == '__main__':
    app.run(debug=True)
