from flask import Flask, render_template, request, redirect, url_for, jsonify, g
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
DATABASE = 'database.db'

# Initialize database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Create database tables if not exists
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                category TEXT,
                date TEXT,
                description TEXT,
                dislikes INTEGER DEFAULT 0
            )
        ''')
        db.commit()

# Route for home page
@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM reviews ORDER BY dislikes DESC')
    reviews = cursor.fetchall()
    return render_template('index.html', reviews=reviews)

# Route for submitting a new review
@app.route('/submit-review', methods=['GET', 'POST'])
def submit_review():
    if request.method == 'POST':
        product_name = request.form['product_name']
        category = request.form['category']
        description = request.form['description']
        date = datetime.now().strftime("%Y-%m-%d")

        if not (product_name and category and description):
            return jsonify({'error': 'Incomplete data provided'}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO reviews (product_name, category, date, description)
            VALUES (?, ?, ?, ?)
        ''', (product_name, category, date, description))
        db.commit()

        return redirect(url_for('home'))

    return render_template('submit_review.html')

# Route for disliking a review
@app.route('/dislike-review/<int:review_id>', methods=['PUT'])
def dislike_review(review_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE reviews
        SET dislikes = dislikes + 1
        WHERE id = ?
    ''', (review_id,))
    db.commit()

    return jsonify({'message': 'Review disliked successfully'}), 200

# Error handling for 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Initialize the database and run the application
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
