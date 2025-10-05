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
    ticker TEXT,
    type TEXT CHECK(type IN ('buy', 'sell')),
    price NUMERIC,
    shares NUMERIC,
    date DATE,
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);

CREATE TABLE IF NOT EXISTS account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,
    date DATE,
    cash_flow NUMERIC,
    FOREIGN KEY (strategy_id) REFERENCES strategy(id)
);