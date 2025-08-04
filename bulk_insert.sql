-- Insert 10 restaurants
INSERT INTO restaurants (id, name, cuisine, owner) VALUES
(1, 'McDonalds', 'American', 'admin'),
(2, 'Dominos', 'American', 'admin'),
(3, 'Pizza Hut', 'American', 'admin'),
(4, 'WoK Momos', 'Indian', 'admin'),
(5, 'KFC', 'American', 'admin'),
(6, 'Papa Jones', 'American', 'admin'),
(7, 'Biryani House', 'Indian', 'admin'),
(8, 'Haldiram', 'Indian', 'admin'),
(9, 'Subway', 'American', 'admin'),
(10, 'Cafe Coffee Day', 'Indian', 'admin');

-- Insert menu items
INSERT INTO menu (restaurant_id, name, price, veg, allergens) VALUES
(1, 'Big Mac', 150, 0, ''),
(1, 'McDouble', 120, 0, ''),
(1, 'McVeggie', 130, 1, ''),
(2, 'Pepperoni Pizza', 400, 0, ''),
(2, 'Veggie Supreme', 350, 1, ''),
(2, 'Cheese Burst', 450, 0, ''),
(3, 'Chicken Supreme', 420, 0, ''),
(3, 'Margherita', 300, 1, ''),
(3, 'Pasta', 350, 1, ''),
(4, 'Steamed Momos', 90, 1, 'gluten'),
(4, 'Fried Momos', 110, 0, 'gluten'),
(5, 'Hot Wings', 220, 0, ''),
(5, 'Veg Burger', 150, 1, ''),
(6, 'Chicken Pizza', 430, 0, ''),
(6, 'Veg Pizza', 380, 1, ''),
(7, 'Hyderabadi Biryani', 250, 0, ''),
(7, 'Veg Biryani', 200, 1, ''),
(8, 'Samosa', 40, 1, ''),
(8, 'Chaat', 60, 1, ''),
(9, 'Chicken Sub', 300, 0, ''),
(9, 'Veg Sub', 250, 1, ''),
(10, 'Coffee', 120, 1, ''),
(10, 'Sandwich', 140, 1, '');
