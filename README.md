# Library-Books-Authors-Members-and-Loans

Python + Flask + MySQL website with six search pages (F2.1 to F2.6).

## What is in this folder

| File | What it does |
|---|---|
| `problem2_DDL.sql` | Creates the `library` database: author, publisher, category, book, member, loan (primary keys, foreign keys, `ON DELETE CASCADE`) |
| `problem2_DML.sql` | Seed data: 5 authors, 3 publishers, 3 categories, 10 books, 5 members, 12 loans |
| `problem2_Queries.sql` | The SQL of every page, each one after a `-- F2.x` comment |
| `website/` | The Flask website |

## How to run it, step by step

1. **Install** Python 3 and MySQL Server, and make sure MySQL is running.
2. **Open a terminal in this folder** (`lab4-<student-id>`).
3. **Build the database, insert the seed data, and try the queries:**
   ```
   mysql -u root -p < problem2_DDL.sql
   mysql -u root -p < problem2_DML.sql
   mysql -u root -p < problem2_Queries.sql
   ```
4. **Install the Python packages:**
   ```
   cd website
   pip install -r requirements.txt
   ```
5. **Tell the website your MySQL password.** Either write it in `DB_CONFIG` inside `website/app.py`,
   or set it in the terminal first:
   - Windows (cmd): `set DB_PASSWORD=your-password`
   - Windows (PowerShell): `$env:DB_PASSWORD="your-password"`
   - Mac / Linux: `export DB_PASSWORD=your-password`
6. **Start the website:** `python app.py`
7. **Open** http://127.0.0.1:5000 in your browser.

## Pages

| Page | Address | What it shows |
|---|---|---|
| F2.1 Search books | `/search` | Title keyword (LIKE), min and max price (BETWEEN), category list; cheapest first |
| F2.2 Catalogue | `/catalogue` | Books with author, publisher and category names (JOIN) |
| F2.3 Reports | `/reports` | Books and average price per category; authors with 2+ books; total, smallest and largest price |
| F2.4 Loans | `/loans` | Loans not returned; members who never borrowed; books never borrowed |
| F2.5 Most borrowed | `/borrowed` | Top 3 books and the member with the most loans |
| F2.6 Authors and books | `/authors-books` | Books per author (including 0); books whose author and publisher share a country |

Every page has a "Show the SQL" box with the query it ran.

## Bonus: prepared statements

The F2.1 search form never puts what the user typed inside the SQL text. The query uses `%s`
placeholders and the values are sent separately (`run(sql, params, prepared=True)` in `app.py`),
so a title like `' OR 1=1 --` is just text.

## Notes

- Running `problem2_DDL.sql` again resets the database.
- Lab 3 pages (add, edit, remove) are not graded again and are not part of this folder.
