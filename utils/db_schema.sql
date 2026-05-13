-- SQLite schema for Campus Lost & Found Management System

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    last_seen_location TEXT,
    date_lost TEXT,
    contact_info TEXT,
    image TEXT,
    status TEXT DEFAULT 'Open',
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS found_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    found_location TEXT,
    date_found TEXT,
    deposited_at TEXT,
    image TEXT,
    status TEXT DEFAULT 'Open',
    FOREIGN KEY(user_id) REFERENCES users(id)
);
