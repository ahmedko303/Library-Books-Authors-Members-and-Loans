USE library;

-- 5 authors: two from Egypt, one with no books (Achebe), three who wrote 2+ books
INSERT INTO author (author_id, name, country) VALUES
  (1, 'Naguib Mahfouz', 'Egypt'),
  (2, 'Taha Hussein',   'Egypt'),
  (3, 'Jane Austen',    'United Kingdom'),
  (4, 'Haruki Murakami','Japan'),
  (5, 'Chinua Achebe',  'Nigeria');

-- 3 publishers: each one shares its country with an author
INSERT INTO publisher (publisher_id, name, country) VALUES
  (1, 'Dar El Shorouk', 'Egypt'),
  (2, 'Penguin Books',  'United Kingdom'),
  (3, 'Kodansha',       'Japan');

INSERT INTO category (category_id, name) VALUES
  (1, 'Fiction'),
  (2, 'Classics'),
  (3, 'Non-fiction');

-- 10 books: Sugar Street (15.50) and Kafka on the Shore (17.90) cost between 15 and 20
-- Persuasion is never borrowed
INSERT INTO book (book_id, title, price, publish_year, author_id, publisher_id, category_id) VALUES
  (1,  'Palace Walk',              14.50, 1956, 1, 1, 2),
  (2,  'Midaq Alley',              11.00, 1947, 1, 1, 1),
  (3,  'Sugar Street',             15.50, 1957, 1, 1, 2),
  (4,  'The Days',                 12.00, 1929, 2, 1, 3),
  (5,  'The Call of the Curlew',   12.50, 1934, 2, 1, 1),
  (6,  'Pride and Prejudice',       9.99, 1813, 3, 2, 2),
  (7,  'Emma',                     10.50, 1815, 3, 2, 2),
  (8,  'Persuasion',               11.75, 1817, 3, 2, 2),
  (9,  'Norwegian Wood',           13.00, 1987, 4, 3, 1),
  (10, 'Kafka on the Shore',       17.90, 2002, 4, 2, 1);

-- Karim Fathy (member 5) has no loans
INSERT INTO member (member_id, name, email, join_date) VALUES
  (1, 'Omar Hassan',  'omar.hassan@example.com',  '2026-01-10'),
  (2, 'Mariam Adel',  'mariam.adel@example.com',  '2026-02-03'),
  (3, 'Youssef Nabil','youssef.nabil@example.com','2026-03-15'),
  (4, 'Salma Reda',   'salma.reda@example.com',   '2026-05-21'),
  (5, 'Karim Fathy',  'karim.fathy@example.com',  '2026-09-01');

-- 12 loans: loans 4, 7 and 12 are not returned yet (return_date is NULL)
INSERT INTO loan (loan_id, book_id, member_id, loan_date, return_date) VALUES
  (1,  1,  1, '2026-09-01', '2026-09-10'),
  (2,  1,  2, '2026-09-12', '2026-09-20'),
  (3,  1,  1, '2026-10-01', '2026-10-08'),
  (4,  1,  3, '2026-10-15', NULL),
  (5,  6,  1, '2026-09-05', '2026-09-18'),
  (6,  6,  2, '2026-10-02', '2026-10-12'),
  (7,  6,  4, '2026-10-20', NULL),
  (8,  9,  3, '2026-09-25', '2026-10-05'),
  (9,  9,  1, '2026-10-25', '2026-11-02'),
  (10, 2,  2, '2026-10-10', '2026-10-17'),
  (11, 4,  4, '2026-11-01', '2026-11-09'),
  (12, 10, 3, '2026-11-05', NULL);
