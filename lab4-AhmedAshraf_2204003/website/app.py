import os
from datetime import date
from decimal import Decimal, InvalidOperation

import mysql.connector
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "library-secret"  # needed for flash messages

# ---- Database settings:  ----
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "303120"),
    "database": "library",
}


# ---------- helpers ----------
def tidy(rows):
    """Make values easy to show: prices with 2 decimals, NULL as '-'."""
    clean = []
    for row in rows:
        new = {}
        for key, value in row.items():
            if isinstance(value, (bytes, bytearray)):
                value = value.decode()
            if value is None:
                value = "-"
            elif isinstance(value, (Decimal, float)):
                value = f"{value:.2f}"
            elif isinstance(value, date):
                value = value.isoformat()
            new[key] = value
        clean.append(new)
    return clean


def run(sql, params=(), prepared=False):
    """Run one SELECT and return the rows as dictionaries.
    prepared=True uses a prepared statement (placeholders %s), see F2.1."""
    conn = mysql.connector.connect(**DB_CONFIG)
    if prepared:
        cur = conn.cursor(prepared=True)
        cur.execute(sql, params)
        names = cur.column_names
        rows = [dict(zip(names, r)) for r in cur.fetchall()]
    else:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
    cur.close()
    conn.close()
    return tidy(rows)


def section(label, note, sql):
    """One block of a page: a title, the result of a query, and the SQL itself."""
    return {"label": label, "note": note, "sql": sql.strip(), "rows": run(sql)}


# ---------- Home ----------
@app.route("/")
def index():
    pages = [
        ("F2.1", "Search books", "search", "Title keyword, price range and category."),
        ("F2.2", "Catalogue", "catalogue", "All books with author, publisher and category names."),
        ("F2.3", "Reports", "reports", "Books per category, busy authors and price totals."),
        ("F2.4", "Loans", "loans", "Open loans, idle members and books nobody borrowed."),
        ("F2.5", "Most borrowed", "borrowed", "The top 3 books and the top member."),
        ("F2.6", "Authors and books", "authors_books", "Books per author and same-country books."),
    ]
    return render_template("index.html", pages=pages)


# ---------- F2.1 Search books (WHERE) + bonus: prepared statement ----------
@app.route("/search")
def search():
    categories = run("SELECT category_id, name FROM category ORDER BY name")
    keyword = request.args.get("q", "").strip()
    low_text = request.args.get("min_price", "").strip()
    high_text = request.args.get("max_price", "").strip()
    category = request.args.get("category", "").strip()

    try:
        low = Decimal(low_text) if low_text else Decimal("0")
        high = Decimal(high_text) if high_text else Decimal("1000000")
    except InvalidOperation:
        flash("Prices must be numbers.", "error")
        low, high = Decimal("0"), Decimal("1000000")

    sql = """SELECT b.book_id, b.title, b.price, b.publish_year, c.name AS category
FROM book b
JOIN category c ON b.category_id = c.category_id
WHERE b.title LIKE %s AND b.price BETWEEN %s AND %s"""
    params = [f"%{keyword}%", low, high]
    if category.isdigit():
        sql += " AND b.category_id = %s"
        params.append(int(category))
    sql += "\nORDER BY b.price ASC"

    # the typed values travel as parameters, never inside the SQL text
    rows = run(sql, tuple(params), prepared=True)
    return render_template("search.html", rows=rows, categories=categories, sql=sql,
                           params=params, q=keyword, min_price=low_text,
                           max_price=high_text, category=category)


# ---------- F2.2 Catalogue (JOIN) ----------
@app.route("/catalogue")
def catalogue():
    sections = [section("All books", "Names instead of ids.", """
SELECT b.book_id, b.title, b.price, b.publish_year,
       a.name AS author, p.name AS publisher, c.name AS category
FROM book b
JOIN author a    ON b.author_id = a.author_id
JOIN publisher p ON b.publisher_id = p.publisher_id
JOIN category c  ON b.category_id = c.category_id
ORDER BY b.book_id""")]
    return render_template("sections.html", title="Catalogue", tag="F2.2", sections=sections)


# ---------- F2.3 Reports (GROUP BY, HAVING) ----------
@app.route("/reports")
def reports():
    sections = [
        section("Books and average price of each category", "GROUP BY", """
SELECT c.name AS category, COUNT(b.book_id) AS books, AVG(b.price) AS average_price
FROM category c
LEFT JOIN book b ON b.category_id = c.category_id
GROUP BY c.category_id, c.name"""),
        section("Authors who wrote at least 2 books", "HAVING", """
SELECT a.author_id, a.name, COUNT(*) AS books
FROM author a
JOIN book b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
HAVING COUNT(*) >= 2"""),
        section("The whole library", "Aggregate functions without GROUP BY", """
SELECT COUNT(*) AS books, SUM(price) AS total_price,
       MIN(price) AS smallest_price, MAX(price) AS largest_price
FROM book"""),
    ]
    return render_template("sections.html", title="Reports", tag="F2.3", sections=sections)


# ---------- F2.4 Loans (JOIN, LEFT JOIN) ----------
@app.route("/loans")
def loans():
    sections = [
        section("Loans not returned yet", "return_date IS NULL", """
SELECT l.loan_id, b.title AS book, m.name AS member, l.loan_date
FROM loan l
JOIN book b   ON l.book_id = b.book_id
JOIN member m ON l.member_id = m.member_id
WHERE l.return_date IS NULL
ORDER BY l.loan_date"""),
        section("Members who never borrowed a book", "LEFT JOIN + IS NULL", """
SELECT m.member_id, m.name, m.email
FROM member m
LEFT JOIN loan l ON l.member_id = m.member_id
WHERE l.loan_id IS NULL"""),
        section("Books that were never borrowed", "LEFT JOIN + IS NULL", """
SELECT b.book_id, b.title
FROM book b
LEFT JOIN loan l ON l.book_id = b.book_id
WHERE l.loan_id IS NULL"""),
    ]
    return render_template("sections.html", title="Loans", tag="F2.4", sections=sections)


# ---------- F2.5 Most borrowed (GROUP BY, ORDER BY, LIMIT) ----------
@app.route("/borrowed")
def borrowed():
    sections = [
        section("The 3 books with the most loans", "GROUP BY, ORDER BY, LIMIT 3", """
SELECT b.book_id, b.title, COUNT(*) AS loans
FROM book b
JOIN loan l ON l.book_id = b.book_id
GROUP BY b.book_id, b.title
ORDER BY loans DESC, b.title
LIMIT 3"""),
        section("The member with the most loans", "LIMIT 1", """
SELECT m.member_id, m.name, COUNT(*) AS loans
FROM member m
JOIN loan l ON l.member_id = m.member_id
GROUP BY m.member_id, m.name
ORDER BY loans DESC
LIMIT 1"""),
    ]
    return render_template("sections.html", title="Most borrowed", tag="F2.5", sections=sections)


# ---------- F2.6 Authors and books (LEFT JOIN, JOIN) ----------
@app.route("/authors-books")
def authors_books():
    sections = [
        section("Every author with the number of books", "LEFT JOIN keeps authors with 0 books", """
SELECT a.author_id, a.name, COUNT(b.book_id) AS books
FROM author a
LEFT JOIN book b ON b.author_id = a.author_id
GROUP BY a.author_id, a.name
ORDER BY a.author_id"""),
        section("Books whose author and publisher come from the same country", "JOIN with a country test", """
SELECT b.book_id, b.title, a.name AS author, p.name AS publisher, a.country
FROM book b
JOIN author a    ON b.author_id = a.author_id
JOIN publisher p ON b.publisher_id = p.publisher_id
WHERE a.country = p.country"""),
    ]
    return render_template("sections.html", title="Authors and books", tag="F2.6", sections=sections)


if __name__ == "__main__":
    app.run(debug=True)
