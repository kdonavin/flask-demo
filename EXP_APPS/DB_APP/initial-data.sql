-- sqlite3 library.db < initial-data.sql

-- Countries
INSERT INTO country (id, name) VALUES (1, 'United States');
INSERT INTO country (id, name) VALUES (2, 'England');
INSERT INTO country (id, name) VALUES (3, 'Argentina');
INSERT INTO country (id, name) VALUES (4, 'Scotland');
-- Authors
INSERT INTO author (id, country_id, name) VALUES (1, 1, 'Edgar Allan Poe');
INSERT INTO author (id, country_id, name) VALUES (2, 1, 'Mark Twain');
INSERT INTO author (id, country_id, name) VALUES (3, 4, 'Arthur Conan Doyle');
INSERT INTO author (id, country_id, name) VALUES (4, 3, 'Jorge Luis Borges');
INSERT INTO author (id, country_id, name) VALUES (5, 1, 'Frank Herbert');
INSERT INTO author (id, country_id, name) VALUES (6, 2, 'J.K. Rowling');
INSERT INTO author (id, country_id, name) VALUES (7, 1, 'Isaac Asimov');
INSERT INTO author (id, country_id, name) VALUES (8, 2, 'George Orwell');
INSERT INTO author (id, country_id, name) VALUES (9, 1, 'H.P. Lovecraft');
-- Books
INSERT INTO book (id, author_id, title, isbn) VALUES (1, 1, 'The Raven', '978-0142437339'); 
INSERT INTO book (id, author_id, title, isbn) VALUES (2, 2, 'The Adventures of Tom Sawyer', '978-0486400778');
INSERT INTO book (id, author_id, title, isbn) VALUES (3, 3, 'The Hound of the Baskervilles', '978-1505255607');
INSERT INTO book (id, author_id, title, isbn) VALUES (4, 4, 'Ficciones', '978-8420658321');
INSERT INTO book (id, author_id, title, isbn) VALUES (5, 5, 'Dune', '978-0441013593');
INSERT INTO book (id, author_id, title, isbn) VALUES (6, 6, 'Harry Potter and the Sorcerer''s Stone', '978-0590353427');
INSERT INTO book (id, author_id, title, isbn) VALUES (7, 7, 'Foundation', '978-0553293357');
INSERT INTO book (id, author_id, title, isbn) VALUES (8, 8, '1984', '978-0451524935');
INSERT INTO book (id, author_id, title, isbn) VALUES (9, 9, 'The Call of Cthulhu', '978-1512091083');
