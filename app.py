import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB = "expenses.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )"""
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = get_db()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC").fetchall()
    total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
    by_category = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses GROUP BY category ORDER BY total DESC"
    ).fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses, total=total, by_category=by_category)


@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"].strip()
    amount = float(request.form["amount"])
    category = request.form["category"]
    date = request.form["date"]
    conn = get_db()
    conn.execute(
        "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
        (title, amount, category, date),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit(expense_id):
    conn = get_db()
    if request.method == "POST":
        conn.execute(
            "UPDATE expenses SET title=?, amount=?, category=?, date=? WHERE id=?",
            (
                request.form["title"].strip(),
                float(request.form["amount"]),
                request.form["category"],
                request.form["date"],
                expense_id,
            ),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    expense = conn.execute("SELECT * FROM expenses WHERE id=?", (expense_id,)).fetchone()
    conn.close()
    if expense is None:
        return redirect(url_for("index"))
    return render_template("edit.html", e=expense)


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete(expense_id):
    conn = get_db()
    conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
