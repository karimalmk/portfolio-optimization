CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cash REAL DEFAULT 0,
    total_value REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS portfolio (
    strategy_id INTEGER NOT NULL,
    ticker TEXT NOT NULL,
    shares REAL DEFAULT 0,
    UNIQUE(strategy_id, ticker),
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('buy', 'sell', 'deposit', 'withdraw')) NOT NULL,
    ticker TEXT,
    shares REAL,
    price REAL,
    date TEXT NOT NULL,
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);
