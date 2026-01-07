ALTER TABLE products
ADD COLUMN category_id INTEGER NOT NULL,
ADD FOREIGN KEY (category_id) REFERENCES categories(id);