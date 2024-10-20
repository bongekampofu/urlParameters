from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

DATABASE_PATH = 'C:\\Users\\Bongeka.Mpofu\\DB Browser for SQLite\\database.db'


# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create food table with price column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            details TEXT NOT NULL,
            price REAL NOT NULL  -- Price column added
        )
    ''')

    # Create cart table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (food_id) REFERENCES food (id)
        )
    ''')

    # Add some sample data if the food table is empty
    cursor.execute('SELECT COUNT(*) FROM food')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO food (name, details, price) VALUES (?, ?, ?)',
                       ('Pizza', 'Stone baked, chicken and mushroom pizza', 9.99))
        cursor.execute('INSERT INTO food (name, details, price) VALUES (?, ?, ?)',
                       ('Burger', 'Juicy beef burger with cheese', 7.49))
        cursor.execute('INSERT INTO food (name, details, price) VALUES (?, ?, ?)',
                       ('Pasta', 'Creamy Alfredo pasta with mushrooms', 8.99))

    conn.commit()
    conn.close()


@app.route('/')
def index():
    # Fetch food items from the database to display
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM food')
    food_items = cursor.fetchall()
    conn.close()
    return render_template('index.html', food_items=food_items)


@app.route('/add_to_cart/<int:food_id>', methods=['POST'])
def add_to_cart(food_id):
    quantity = request.form.get('quantity', default=1, type=int)  # Get quantity from the form

    # Debugging output
    print(f"Adding to cart - Food ID: {food_id}, Quantity: {quantity}")

    # Insert or update the cart in the database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Check if the food item already exists in the cart
    cursor.execute('SELECT quantity FROM cart WHERE food_id = ?', (food_id,))
    row = cursor.fetchone()
    if row:
        # If it exists, update the quantity
        new_quantity = row[0] + quantity
        cursor.execute('UPDATE cart SET quantity = ? WHERE food_id = ?', (new_quantity, food_id))
    else:
        # Otherwise, insert a new entry
        cursor.execute('INSERT INTO cart (food_id, quantity) VALUES (?, ?)', (food_id, quantity))

    conn.commit()
    conn.close()
    return redirect(url_for('index'))  # Redirect back to the index page


@app.route('/view_cart')
def view_cart():
    # Retrieve items from the cart
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT food_id, quantity FROM cart')
    cart_items = cursor.fetchall()

    food_details = []
    for food_id, quantity in cart_items:
        cursor.execute('SELECT * FROM food WHERE id = ?', (food_id,))
        food_item = cursor.fetchone()
        if food_item:
            food_details.append(
                {'id': food_item[0], 'name': food_item[1], 'details': food_item[2], 'price': food_item[3], 'quantity': quantity})

    conn.close()
    return render_template('view_cart.html', food_details=food_details)


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
