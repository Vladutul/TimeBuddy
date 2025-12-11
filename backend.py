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

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            hours REAL NOT NULL,
            description TEXT,
            project_id INTEGER REFERENCES projects(id)
        )
    """)
    db.commit()

@app.route("/api/projects", methods=["GET"])
def list_projects():
    db = get_db()
    rows = db.execute("SELECT * FROM projects ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.json
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Project name required"}), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO projects(name) VALUES (?)", (name,))
        db.commit()
        return jsonify({"id": cur.lastrowid, "name": name}), 201
    except:
        return jsonify({"error": "Project already exists"}), 400

@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    db = get_db()
    db.execute("UPDATE time_entries SET project_id = NULL WHERE project_id = ?", (project_id,))
    db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.commit()
    return "", 204

@app.route("/api/time-entries", methods=["GET"])
def list_entries():
    db = get_db()
    rows = db.execute("""
        SELECT t.id, t.date, t.hours, t.description,
               p.id as project_id, p.name as project_name
        FROM time_entries t
        LEFT JOIN projects p ON t.project_id = p.id
        ORDER BY t.date DESC
    """).fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/time-entries", methods=["POST"])
def create_entry():
    data = request.json
    date = data.get("date")
    hours = data.get("hours")
    description = data.get("description", "")
    project_id = data.get("project_id")  # optional

    if not date or hours is None:
        return jsonify({"error": "Missing fields"}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO time_entries(date, hours, description, project_id) VALUES (?, ?, ?, ?)",
        (date, hours, description, project_id)
    )
    db.commit()
    new_id = cur.lastrowid
    return jsonify({"id": new_id, "date": date, "hours": hours, "description": description, "project_id": project_id}), 201

@app.route("/api/time-entries/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    db = get_db()
    db.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    db.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
