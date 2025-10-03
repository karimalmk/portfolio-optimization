UPDATE price_data
    SET volume = CAST(volume AS INTEGER);

SELECT volume FROM price_data
    WHERE volume > 100000000
    ORDER BY volume DESC
    LIMIT 20;

-- sqlite3 my_database.db < queries.sql -- from ubuntu shell (shells in general)
-- .read queries.sql -- from the sqlite3 command-line interface