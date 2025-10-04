CREATE TABLE IF NOT EXISTS strategy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    cash NUMERIC
);

CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy TEXT NOT NULL,
    symbol TEXT,
    shares INTEGER,
    FOREIGN KEY (strategy) REFERENCES strategy(name),
    UNIQUE(strategy, symbol)
);

CREATE TABLE IF NOT EXISTS buy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy TEXT NOT NULL,
    symbol TEXT,
    price NUMERIC,
    shares NUMERIC,
    buy_date DATE,
    FOREIGN KEY (strategy) REFERENCES strategy(name)
);

CREATE TABLE IF NOT EXISTS sell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy TEXT NOT NULL,
    symbol TEXT,
    price NUMERIC,
    shares NUMERIC,
    sell_date DATE,
    FOREIGN KEY (strategy) REFERENCES strategy(name)
);