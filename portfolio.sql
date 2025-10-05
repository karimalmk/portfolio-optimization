CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cash NUMERIC,
    total_value NUMERIC GENERATED ALWAYS AS (cash) VIRTUAL
);

CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    symbol TEXT,
    shares INTEGER,
    UNIQUE(strategy_id, symbol),
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    symbol TEXT,
    type TEXT CHECK(type IN ('buy', 'sell')),
    price NUMERIC,
    shares NUMERIC,
    transaction_date DATE,
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);