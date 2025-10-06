CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cash NUMERIC,
    total_value NUMERIC GENERATED ALWAYS AS (cash) VIRTUAL
);

CREATE TABLE IF NOT EXISTS portfolio (
    strategy_id INTEGER NOT NULL,
    ticker TEXT,
    shares INTEGER,
    UNIQUE(strategy_id, ticker),
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('buy', 'sell', 'deposit')),
    ticker TEXT,
    shares NUMERIC,
    price NUMERIC,
    date DATE NOT NULL,
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);