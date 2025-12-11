import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE = "time.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            description TEXT
        )
    """)
    db.commit()

# GET all entries
@app.route("/api/time-entries", methods=["GET"])
def list_entries():
    db = get_db()
    rows = db.execute("SELECT * FROM time_entries ORDER BY date DESC").fetchall()
    return jsonify([dict(row) for row in rows])

# POST new entry
@app.route("/api/time-entries", methods=["POST"])
def create_entry():
    data = request.json
    date = data.get("date")
    hours = data.get("hours")
    description = data.get("description", "")

    if not date or hours is None:
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO time_entries(date, hours, description) VALUES (?, ?, ?)",
        (date, hours, description)
    )
    db.commit()

    new_id = cur.lastrowid
    return jsonify({"id": new_id, "date": date, "hours": hours, "description": description}), 201

# DELETE entry
@app.route("/api/time-entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    db = get_db()
    db.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    db.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
