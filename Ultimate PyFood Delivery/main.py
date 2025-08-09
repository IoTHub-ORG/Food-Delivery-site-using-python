import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key_final"
DATABASE = os.path.join(app.instance_path, "pyfood.db")
os.makedirs(app.instance_path, exist_ok=True)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, timeout=20)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db:
        db.close()

def init_db():
    db = get_db()
    with app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))
    db.commit()

def seed_db():
    db = get_db()
    # Users
    db.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
               ("admin", generate_password_hash("admin123"), "owner", "admin@food.com"))
    db.execute("INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
               ("alice", generate_password_hash("alicepass"), "customer", "alice@mail.com"))
    db.commit()
    owner_id = db.execute("SELECT id FROM users WHERE username='admin'").fetchone()["id"]
    # Restaurants
    rests = [
        ("McDonalds", "Famous fast food chain", owner_id),
        ("Dominos", "Pizza chain", owner_id),
        ("Pizza Hut", "Italian pizza and pasta", owner_id),
        ("KFC", "Crispy chicken specialists", owner_id),
        ("Subway", "Fresh sandwiches and salads", owner_id)
    ]
    for name, desc, oid in rests:
        db.execute("INSERT INTO restaurants (name, description, owner_id) VALUES (?, ?, ?)", (name, desc, oid))
    db.commit()
    # Menu items
    for rest in db.execute("SELECT id FROM restaurants").fetchall():
        for i in range(1, 16):
            veg = 1 if i % 2 == 0 else 0
            db.execute("INSERT INTO menu (restaurant_id, name, price, veg, allergens) VALUES (?, ?, ?, ?, ?)",
                       (rest["id"], f"Sample Dish {i}", 50 + i*5, veg, ""))
    db.commit()

@app.route("/")
def home():
    return redirect(url_for("restaurants"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        role = "customer"

        if not username or not email or not password:
            flash("Please fill all fields correctly.", "danger")
            return render_template("register.html")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), role, email)
            )
            db.commit()
        except sqlite3.IntegrityError:
            flash("Username or email already exists.", "danger")
            return render_template("register.html")

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Enter both username and password.", "danger")
            return render_template("login.html")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            flash("No such user found.", "danger")
            return render_template("login.html")
        if not check_password_hash(user["password"], password):
            flash("Incorrect password.", "danger")
            return render_template("login.html")
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        flash(f"Welcome {user['username']}!", "success")
        return redirect(url_for("restaurants"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

@app.route("/restaurants")
def restaurants():
    db = get_db()
    rests = db.execute("SELECT id, name, description FROM restaurants").fetchall()
    return render_template("restaurants.html", restaurants=rests)

@app.route("/restaurant/<int:rest_id>", methods=["GET", "POST"])
def restaurant(rest_id):
    db = get_db()
    rest = db.execute("SELECT * FROM restaurants WHERE id=?", (rest_id,)).fetchone()
    if not rest:
        flash("Restaurant not found.", "danger")
        return redirect(url_for("restaurants"))
    menu = db.execute("SELECT * FROM menu WHERE restaurant_id=?", (rest_id,)).fetchall()
    if request.method == "POST":
        menu_id = int(request.form.get("menu_id"))
        qty = int(request.form.get("qty", 1))
        item = db.execute("SELECT * FROM menu WHERE id=?", (menu_id,)).fetchone()
        cart = session.get("cart", [])
        if cart and cart[0]["restaurant_id"] != item["restaurant_id"]:
            flash("Clear cart before adding from another restaurant.", "danger")
            return redirect(url_for("cart"))
        for c in cart:
            if c["id"] == item["id"]:
                c["qty"] += qty
                break
        else:
            cart.append({"id": item["id"], "name": item["name"], "price": item["price"],
                         "qty": qty, "restaurant_id": item["restaurant_id"]})
        session["cart"] = cart
        flash(f"Added {item['name']} to cart.", "success")
        return redirect(url_for("restaurant", rest_id=rest_id))
    return render_template("restaurant.html", rest=rest, menu=menu)
@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "user_id" not in session:
        flash("Please login to place an order.", "warning")
        return redirect(url_for("login"))

    cart = session.get("cart", [])

    if request.method == "POST":
        if "clear_cart" in request.form:
            session["cart"] = []
            flash("Cart cleared.", "info")
            return redirect(url_for("cart"))

        address = request.form.get("address", "").strip()
        contact = request.form.get("contact", "").strip()
        if not address or not contact:
            flash("Please enter both address and contact info.", "danger")
            return redirect(url_for("cart"))
        if not cart:
            flash("Cart is empty.", "danger")
            return redirect(url_for("cart"))

        db = get_db()
        user_id = session["user_id"]
        rest_id = cart[0]["restaurant_id"]
        total = sum(item["price"] * item["qty"] for item in cart)

        db.execute(
            "INSERT INTO orders (user_id, restaurant_id, total, address, contact, status) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, rest_id, total, address, contact, "Pending"),
        )
        order_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        for item in cart:
            db.execute(
                "INSERT INTO order_items (order_id, menu_id, qty) VALUES (?, ?, ?)",
                (order_id, item["id"], item["qty"])
            )
        db.commit()
        session["cart"] = []
        flash("Order placed successfully.", "success")
        return redirect(url_for("thank_you"))

    return render_template("cart.html", cart=cart, total=sum(item["price"] * item["qty"] for item in cart))

@app.route("/thank_you")
def thank_you():
    return render_template("thank_you.html")



@app.route("/orders")
def orders():
    db = get_db()
    user_id = session.get("user_id")
    all_orders = db.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (user_id,)).fetchall()
    out = []
    for o in all_orders:
        items = db.execute("SELECT m.name, oi.qty FROM order_items oi JOIN menu m ON oi.menu_id=m.id WHERE oi.order_id=?", (o["id"],)).fetchall()
        out.append({"order": o, "items": items})
    return render_template("orders.html", orders=out)

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
            seed_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)

