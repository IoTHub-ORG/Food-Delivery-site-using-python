print("Welcome to Ultimate PyFood Delivery Console App!\n")

users = []
restaurants = []
orders = []

session_user = None
session_role = None
restaurant_id_counter = 1
order_id_counter = 1
session_cart = []

def find_user(username):
    for user in users:
        if user['username'] == username:
            return user
    return None

def get_restaurant_by_id(rid):
    for r in restaurants:
        if r['id'] == rid:
            return r
    return None

def input_int(msg, min_val=None, max_val=None):
    while True:
        val = input(msg)
        if val.isdigit():
            val = int(val)
            if (min_val is None or val >= min_val) and (max_val is None or val <= max_val):
                return val
        print("Invalid input. Enter number ", end='')
        if min_val is not None: print(f">= {min_val} ", end='')
        if max_val is not None: print(f"and <= {max_val}", end='')
        print(".")

def print_line():
    print("="*50)

def pause():
    input("Press Enter to continue...")

def register_customer():
    print_line()
    print("Register as Customer")
    while True:
        username = input("Username: ").strip()
        if not username:
            print("Cannot be empty.")
            continue
        if find_user(username):
            print("Username taken.")
            continue
        break
    password = input("Password: ").strip()
    allergies = input("List allergens (comma separated or blank): ").strip()
    allergen_set = set(a.strip().lower() for a in allergies.split(",") if a.strip()) if allergies else set()
    profile = {'allergens': allergen_set}
    users.append({'username': username, 'password': password, 'role': 'customer', 'profile': profile})
    print(f"Customer '{username}' registered successfully.\n")
    pause()

def register_restaurant_owner():
    global restaurant_id_counter
    print_line()
    print("Register as Restaurant Owner")
    while True:
        username = input("Username: ").strip()
        if not username:
            print("Cannot be empty.")
            continue
        if find_user(username):
            print("Username taken.")
            continue
        break
    password = input("Password: ").strip()
    rest_name = input("Restaurant name: ").strip()
    cuisine = input("Cuisine type: ").strip()
    users.append({'username': username, 'password': password, 'role': 'restaurant', 
                  'profile': {'restaurant_name': rest_name, 'cuisine': cuisine}})
    restaurants.append({'id': restaurant_id_counter, 'name': rest_name, 'owner': username,
                        'cuisine': cuisine, 'menu': []})
    print(f"Restaurant '{rest_name}' registered with owner '{username}'.\n")
    restaurant_id_counter += 1
    pause()

def login():
    global session_user, session_role
    print_line()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = find_user(username)
    if not user or user['password'] != password:
        print("Invalid credentials.\n")
        pause()
        return False
    session_user = username
    session_role = user['role']
    print(f"Welcome {username}! Role: {session_role}\n")
    pause()
    return True

def logout():
    global session_user, session_role, session_cart
    session_user = None
    session_role = None
    session_cart = []
    print("Logged out.\n")
    pause()

def get_owner_restaurant():
    for r in restaurants:
        if r['owner'] == session_user:
            return r
    return None

def add_menu_item(restaurant):
    print_line()
    name = input("Item name: ").strip()
    price = input_int("Price (₹): ", 1)
    veg = input("Vegetarian? (y/n): ").strip().lower() == 'y'
    allergens = input("Allergens (comma separated or blank): ").strip()
    allergen_set = set(a.strip().lower() for a in allergens.split(",") if a.strip()) if allergens else set()
    restaurant['menu'].append({'item': name, 'price': price, 'veg': veg, 'allergens': allergen_set})
    print(f"Added '{name}' to menu.\n")
    pause()

def edit_menu_item(restaurant):
    if not restaurant['menu']:
        print("Menu empty.\n")
        pause()
        return
    print_line()
    for i,itm in enumerate(restaurant['menu'],1):
        veg_str = "Veg" if itm['veg'] else "Non-Veg"
        alg = ', '.join(itm['allergens']) if itm['allergens'] else 'None'
        print(f"{i}. {itm['item']} - ₹{itm['price']} [{veg_str}] Allergens: {alg}")
    choice = input_int(f"Choose item to edit (1-{len(restaurant['menu'])}): ",1,len(restaurant['menu']))-1
    item = restaurant['menu'][choice]
    new_name = input(f"New name or blank to keep '{item['item']}': ").strip()
    if new_name:
        item['item'] = new_name
    new_price = input(f"New price or blank to keep ₹{item['price']}: ").strip()
    if new_price.isdigit():
        item['price'] = int(new_price)
    new_veg = input(f"Vegetarian (y/n or blank to keep {'y' if item['veg'] else 'n'}): ").strip().lower()
    if new_veg == 'y':
        item['veg'] = True
    elif new_veg == 'n':
        item['veg'] = False
    new_allergens = input(f"New allergens or blank to keep current ({', '.join(item['allergens']) if item['allergens'] else 'None'}): ").strip()
    if new_allergens:
        item['allergens'] = set(a.strip().lower() for a in new_allergens.split(",") if a.strip())
    print("Item updated.\n")
    pause()

def remove_menu_item(restaurant):
    if not restaurant['menu']:
        print("Menu empty.\n")
        pause()
        return
    print_line()
    for i,itm in enumerate(restaurant['menu'],1):
        print(f"{i}. {itm['item']}")
    choice = input_int(f"Select item to remove (1-{len(restaurant['menu'])}): ",1,len(restaurant['menu'])) -1
    removed = restaurant['menu'].pop(choice)
    print(f"Removed '{removed['item']}' from menu.\n")
    pause()

def owner_menu():
    while True:
        restaurant = get_owner_restaurant()
        if not restaurant:
            print("No restaurant profile found.\n")
            pause()
            return
        print_line()
        print(f"Owner Menu - {session_user} ({restaurant['name']})")
        print("1. Add Menu Item\n2. Edit Menu Item\n3. Remove Menu Item\n4. Logout")
        choice = input_int("Option: ",1,4)
        if choice == 1:
            add_menu_item(restaurant)
        elif choice == 2:
            edit_menu_item(restaurant)
        elif choice == 3:
            remove_menu_item(restaurant)
        elif choice == 4:
            logout()
            break

def browse_restaurants():
    while True:
        print_line()
        print("Browse Restaurants")
        print("Filters:")
        print("1. Show All")
        print("2. Filter by Cuisine")
        print("3. Filter Vegetarian Only")
        print("4. Back to Customer Menu")
        choice = input_int("Choose filter: ",1,4)
        filtered = restaurants
        if choice == 2:
            c = input("Enter cuisine to filter by (case insensitive): ").strip().lower()
            filtered = [r for r in restaurants if r['cuisine'].lower() == c]
        elif choice ==3:
            filtered = [r for r in restaurants if any(item['veg'] for item in r['menu'])]
        elif choice ==4:
            return
        if not filtered:
            print("No restaurants found with these filters.")
            pause()
            continue
        print("Restaurants:")
        for r in filtered:
            print(f"{r['id']}. {r['name']} ({r['cuisine']}) - {len(r['menu'])} items")
        rid = input_int("Enter restaurant ID to view menu (0 to back): ")
        if rid == 0:
            continue
        restaurant = get_restaurant_by_id(rid)
        if not restaurant:
            print("Invalid restaurant ID.")
            pause()
            continue
        browse_menu_and_add_to_cart(restaurant)

def browse_menu_and_add_to_cart(restaurant):
    global session_cart
    user_obj = find_user(session_user)
    user_allergens = user_obj['profile']['allergens'] if user_obj and 'profile' in user_obj and 'allergens' in user_obj['profile'] else set()
    while True:
        print_line()
        print(f"{restaurant['name']} Menu:")
        if not restaurant['menu']:
            print("No items available.")
            pause()
            return
        for i, item in enumerate(restaurant['menu'],1):
            veg_str = "Veg" if item['veg'] else "Non-Veg"
            allergen_warn = " (!)" if user_allergens.intersection(item['allergens']) else ""
            print(f"{i}. {item['item']} - ₹{item['price']} [{veg_str}]{allergen_warn}")
        print("0. Back to restaurant list")
        choice = input_int("Choose item to add to cart: ",0,len(restaurant['menu']))
        if choice ==0:
            return
        qty = input_int("Quantity: ",1)
        item = restaurant['menu'][choice-1]
        if user_allergens.intersection(item['allergens']):
            print("Warning: Item contains your allergens!")
            cont = input("Add anyway? (y/n): ").strip().lower()
            if cont != 'y':
                continue
        if session_cart and session_cart[0]['restaurant_id'] != restaurant['id']:
            print("You have items from another restaurant in your cart.")
            clr = input("Clear cart and start new order? (y/n): ").strip().lower()
            if clr == 'y':
                session_cart.clear()
            else:
                continue
        existing = None
        for c in session_cart:
            if c['item'] == item['item']:
                existing = c
                break
        if existing:
            existing['qty'] += qty
        else:
            session_cart.append({'restaurant_id': restaurant['id'], 'item': item['item'], 'qty': qty, 'price': item['price']})
        print(f"Added {qty} x {item['item']} to cart.\n")
        pause()

def view_cart():
    global session_cart
    if not session_cart:
        print_line()
        print("Cart is empty.")
        pause()
        return
    print_line()
    print("Your Cart:")
    rest = get_restaurant_by_id(session_cart[0]['restaurant_id'])
    print(f"Restaurant: {rest['name']}")
    total = 0
    for i,c in enumerate(session_cart,1):
        print(f"{i}. {c['item']} x{c['qty']} @ ₹{c['price']} each = ₹{c['qty']*c['price']}")
        total += c['qty']*c['price']
    print(f"Total: ₹{total}")
    print("Options:")
    print("1. Remove Item")
    print("2. Update Quantity")
    print("3. Place Order")
    print("4. Clear Cart")
    print("0. Back to Customer Menu")
    choice = input_int("Choose option: ",0,4)
    if choice == 1:
        rm_idx = input_int(f"Choose item number to remove (1-{len(session_cart)}): ",1,len(session_cart)) -1
        removed = session_cart.pop(rm_idx)
        print(f"Removed {removed['item']} from cart.")
        pause()
    elif choice == 2:
        up_idx = input_int(f"Choose item number to update (1-{len(session_cart)}): ",1,len(session_cart)) -1
        new_qty = input_int("Enter new quantity: ",1)
        session_cart[up_idx]['qty'] = new_qty
        print("Quantity updated.")
        pause()
    elif choice == 3:
        place_order()
    elif choice == 4:
        session_cart.clear()
        print("Cart cleared.")
        pause()
    elif choice == 0:
        return

def place_order():
    global order_id_counter, session_cart, orders
    if not session_cart:
        print("Cart empty, cannot place order.")
        pause()
        return
    total = sum(c['qty']*c['price'] for c in session_cart)
    print_line()
    print(f"Placing order. Total: ₹{total}")
    confirm = input("Confirm order? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Order cancelled.")
        pause()
        return
    order = {
        'order_id': order_id_counter,
        'customer': session_user,
        'restaurant_id': session_cart[0]['restaurant_id'],
        'items': [c.copy() for c in session_cart],
        'status': 'preparing',
        'total': total
    }
    orders.append(order)
    order_id_counter +=1
    session_cart.clear()
    print(f"Order placed successfully! Order ID: {order['order_id']}, Status: {order['status']}")
    pause()

def view_order_history():
    print_line()
    print("Your Orders:")
    user_orders = [o for o in orders if o['customer'] == session_user]
    if not user_orders:
        print("No past orders.")
        pause()
        return
    for o in user_orders:
        r = get_restaurant_by_id(o['restaurant_id'])
        print(f"Order ID: {o['order_id']} from {r['name']} - Status: {o['status']} - Total: ₹{o['total']}")
        print("Items:")
        for it in o['items']:
            print(f"  {it['item']} x{it['qty']} @ ₹{it['price']}")
        print_line()
    pause()

def customer_menu():
    while True:
        print_line()
        print(f"Customer Menu - {session_user}")
        print("1. Browse Restaurants")
        print("2. View Cart")
        print("3. Order History")
        print("4. Logout")
        choice = input_int("Choose option: ",1,4)
        if choice ==1:
            browse_restaurants()
        elif choice ==2:
            view_cart()
        elif choice ==3:
            view_order_history()
        elif choice ==4:
            logout()
            break

def main_menu():
    while True:
        print_line()
        print("Ultimate PyFood Delivery")
        if not session_user:
            print("1. Register as Customer")
            print("2. Register as Restaurant Owner")
            print("3. Login")
            print("4. Exit")
            choice = input_int("Enter choice: ",1,4)
            if choice == 1:
                register_customer()
            elif choice == 2:
                register_restaurant_owner()
            elif choice == 3:
                if login():
                    if session_role == 'restaurant':
                        owner_menu()
                    else:
                        customer_menu()
            else:
                print("Goodbye!")
                break
        else:
            if session_role == 'restaurant':
                owner_menu()
            else:
                customer_menu()

if __name__ == "__main__":
    main_menu()
