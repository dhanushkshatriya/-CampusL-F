-- Sample data for testing
INSERT INTO users (name, email, department, password_hash, role) VALUES
('Alice Smith', 'alice@univ.edu', 'CSE', 'pbkdf2:sha256:260000$test$testhash', 'student'),
('Bob Admin', 'admin@univ.edu', 'Admin', 'pbkdf2:sha256:260000$test$testhash', 'admin');

INSERT INTO lost_items (user_id, item_name, category, description, last_seen_location, date_lost, contact_info, image, status) VALUES
(1, 'Black Wallet', 'Accessories', 'Lost near library', 'Library', '2026-05-01', 'alice@univ.edu', 'wallet.jpg', 'Open'),
(1, 'Blue Water Bottle', 'Bottles', 'Left in canteen', 'Canteen', '2026-05-05', 'alice@univ.edu', 'bottle.jpg', 'Recovered');

INSERT INTO found_items (user_id, item_name, category, description, found_location, date_found, deposited_at, image, status) VALUES
(2, 'Black Wallet', 'Accessories', 'Found near library', 'Library', '2026-05-02', 'Security Office', 'wallet.jpg', 'Open');
