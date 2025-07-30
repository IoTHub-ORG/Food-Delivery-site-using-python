print("Welcome to Ultimate PyFood Delivery Console App!\n")

users = []
restaurants = []
session_user = None
session_role = None
restaurant_id_counter = 1

def find_user(username):
    for user in users:
        if user['username'] == username:
            return user
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
    print("="*40)

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

def login():
    global session_user, session_role
    print_line()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    user = find_user(username)
    if not user or user['password'] != password:
        print("Invalid credentials.\n")
        return False
    session_user = username
    session_role = user['role']
    print(f"Welcome {username}! Role: {session_role}\n")
    return True

def logout():
    global session_user, session_role
    session_user = None
    session_role = None
    print("Logged out.\n")

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

def edit_menu_item(restaurant):
    if not restaurant['menu']:
        print("Menu empty.\n")
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

def remove_menu_item(restaurant):
    if not restaurant['menu']:
        print("Menu empty.\n")
        return
    print_line()
    for i,itm in enumerate(restaurant['menu'],1):
        print(f"{i}. {itm['item']}")
    choice = input_int(f"Select item to remove (1-{len(restaurant['menu'])}): ",1,len(restaurant['menu'])) -1
    removed = restaurant['menu'].pop(choice)
    print(f"Removed '{removed['item']}' from menu.\n")

def owner_menu():
    while True:
        restaurant = get_owner_restaurant()
        if not restaurant:
            print("No restaurant profile found.\n")
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

def main_menu():
    while True:
        print_line()
        print("Ultimate PyFood Delivery")
        if not session_user:
            print("1. Register as Customer\n2. Register as Restaurant Owner\n3. Login\n4. Exit")
            choice = input_int("Enter choice: ",1,4)
            if choice == 1:
                register_customer()
            elif choice == 2:
                register_restaurant_owner()
            elif choice == 3:
                if login():
                    if session_role == 'restaurant': owner_menu()
                    else:
                        print("Customer menu not implemented yet.\n")
                        logout()
            else:
                print("Goodbye!")
                break
        else:
            if session_role == 'restaurant':
                owner_menu()
            else:
                print("Customer menu not implemented yet.\n")
                logout()

if __name__ == "__main__":
    main_menu()
