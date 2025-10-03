CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT,
    price NUMERIC,
    shares NUMERIC,
    purchase_date DATE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creating the sell table
CREATE TABLE IF NOT EXISTS sell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    symbol TEXT,
    price NUMERIC,
    shares NUMERIC,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creating portfolio
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol TEXT NOT NULL,
    shares INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, symbol)   -- ensures no duplicate rows per user
);

-- CREATE UNIQUE INDEX idx_users_username ON users(username);
-- CREATE UNIQUE INDEX idx_users_email ON users(email);
