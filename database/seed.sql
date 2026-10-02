-- Sample seed data for local development / testing

INSERT INTO categories (name) VALUES ('Electronics'), ('Clothing'), ('Books');

INSERT INTO products (name, description, price, stock_quantity, category_id)
VALUES
  ('Wireless Mouse', 'Ergonomic wireless mouse', 19.99, 100, 1),
  ('T-Shirt', '100% cotton t-shirt', 12.50, 200, 2),
  ('Novel: The Great Adventure', 'A thrilling adventure novel', 9.99, 50, 3);
