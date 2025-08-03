import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = "dev_secret"
DATABASE = os.path.join(app.instance_path, "pyfood.db")
os.makedirs(app.instance_path, exist_ok=True)

# Database helpers
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, timeout=10)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource("schema.sql", "r") as f:
        db.executescript(f.read())
    db.commit()

def seed_data():
    db = get_db()
    db.execute("DELETE FROM order_items")
    db.execute("DELETE FROM orders")
    db.execute("DELETE FROM menu")
    db.execute("DELETE FROM restaurants")
    db.execute("DELETE FROM users")
    db.commit()
    db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "adminpass", "restaurant"))
    # Ten sample restaurants with 3 menu items each for brevity
    restaurants = [(1, "McDonalds", "admin"), (2, "Dominos", "admin"), (3, "Pizza Hut", "admin"), (4, "WoK Momos", "admin"), (5, "KFC", "admin")]
    db.executemany("INSERT INTO restaurants (id, name, owner) VALUES (?, ?, ?)", restaurants)
    menus = [
        (1, "Big Mac", 150, 0, ""), (1, "Veggie Burger", 130, 1, ""), (1, "Fries", 60, 1, ""),
        (2, "Margherita", 200, 1, ""), (2, "Pepperoni", 230, 0, ""), (2, "Cheese Burst", 250, 1, ""),
        (3, "Farmhouse", 240, 1, ""), (3, "Chicken Supreme", 290, 0, ""), (3, "Breadsticks", 70, 1, ""),
        (4, "Steamed Momos", 110, 1, ""), (4, "Chicken Momos", 130, 0, ""), (4, "Chilli Momos", 120, 0, ""),
        (5, "Hot Wings", 150, 0, ""), (5, "Veg Zinger", 130, 1, ""), (5, "French Fries", 80, 1, "")
    ]
    db.executemany("INSERT INTO menu (restaurant_id, name, price, veg, allergens) VALUES (?, ?, ?, ?, ?)", menus)
    db.commit()

# Routes
@app.route('/')
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    conn = get_db()
    restaurants = conn.execute("SELECT id, name FROM restaurants").fetchall()
    return render_template("restaurants.html", restaurants=restaurants)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        role = request.form["role"]
        if not username or not password or not role:
            flash("All fields required.", "danger")
            return render_template("register.html")
        conn = get_db()
        try:
            conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
            return render_template("register.html")
        flash("Registered. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user or user["password"] != password:
            flash("Invalid username or password.", "danger")
            return render_template("login.html")
        session["username"] = user["username"]
        session["role"] = user["role"]
        flash(f"Welcome, {username}!", "success")
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route('/restaurant/<int:rest_id>', methods=["GET", "POST"])
def restaurant(rest_id):
    conn = get_db()
    restaurant = conn.execute("SELECT * FROM restaurants WHERE id=?", (rest_id,)).fetchone()
    menu = conn.execute("SELECT * FROM menu WHERE restaurant_id=?", (rest_id,)).fetchall()
    if request.method == "POST":
        item_id = int(request.form["menu_id"])
        qty = int(request.form.get("qty", 1))
        item = conn.execute("SELECT * FROM menu WHERE id=?", (item_id,)).fetchone()
        cart = session.get("cart", [])
        if cart and cart[0]["restaurant_id"] != item["restaurant_id"]:
            flash("Cart contains items from another restaurant. Clear cart first.", "danger")
            return redirect(url_for("cart"))
        for c in cart:
            if c["id"] == item["id"]:
                c["qty"] += qty
                break
        else:
            cart.append({"id": item["id"], "name": item["name"], "price": item["price"], "qty": qty, "restaurant_id": item["restaurant_id"]})
        session["cart"] = cart
        flash(f"Added {item['name']} x{qty}", "success")
    return render_template("restaurant.html", restaurant=restaurant, menu=menu)

@app.route('/cart', methods=["GET", "POST"])
def cart():
    cart = session.get("cart", [])
    if request.method == "POST":
        if not cart:
            flash("Cart empty.", "danger")
            return redirect(url_for("cart"))
        conn = get_db()
        username = session["username"]
        rest_id = cart[0]["restaurant_id"]
        total = sum(item["price"] * item["qty"] for item in cart)
        conn.execute("INSERT INTO orders (username, restaurant_id, total, status) VALUES (?, ?, ?, ?)",
                     (username, rest_id, total, "Placed"))
        order_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for item in cart:
            conn.execute("INSERT INTO order_items (order_id, menu_id, qty) VALUES (?, ?, ?)",
                         (order_id, item["id"], item["qty"]))
        conn.commit()
        session["cart"] = []
        flash("Order placed.", "success")
        return redirect(url_for("orders"))
    return render_template("cart.html", cart=cart, total=sum(i["price"]*i["qty"] for i in cart))

@app.route('/orders')
def orders():
    username = session.get("username")
    conn = get_db()
    orders = conn.execute("SELECT * FROM orders WHERE username=? ORDER BY id DESC", (username,)).fetchall()
    rows = []
    for o in orders:
        items = conn.execute("SELECT m.name, oi.qty FROM order_items oi JOIN menu m ON oi.menu_id=m.id WHERE oi.order_id=?", (o["id"],)).fetchall()
        rows.append({"order": o, "items": items})
    return render_template("orders.html", orders=rows)

if __name__ == "__main__":
    if not os.path.exists(DATABASE) or os.path.getsize(DATABASE) == 0:
        print("Initializing database and seeding data ...")
        with app.app_context():
            init_db()
            seed_data()
    app.run(debug=True)
