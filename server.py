
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "machines.db"

MACHINE_IDS = (
    [f"CNC-{i:02d}" for i in range(1, 26)] +
    [f"VMC-{i:02d}" for i in range(1, 16)]
)

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS machines (
            id TEXT PRIMARY KEY,
            machine_type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OFFLINE',
            part_count INTEGER NOT NULL DEFAULT 0,
            running_signal INTEGER DEFAULT 0,
            alarm_signal INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)

    for machine_id in MACHINE_IDS:
        machine_type = "CNC" if machine_id.startswith("CNC") else "VMC"

        conn.execute("""
            INSERT OR IGNORE INTO machines
            (id, machine_type, status, part_count)
            VALUES (?, ?, 'OFFLINE', 0)
        """, (machine_id, machine_type))

    conn.commit()
    conn.close()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "message": "THE SAPRE TECH Server is running",
        "status": "OK"
    })


@app.route("/api/machine", methods=["POST"])
def update_machine():
    data = request.get_json(silent=True) or {}

    machine_id = data.get("id")
    status = str(data.get("status", "IDLE")).upper()

    if machine_id not in MACHINE_IDS:
        return jsonify({"error": "Invalid machine ID"}), 400

    if status not in ["RUNNING", "IDLE", "ALARM", "OFFLINE"]:
        return jsonify({"error": "Invalid status"}), 400

    try:
        part_count = int(data.get("partCount", 0))
        if part_count < 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid partCount"}), 400

    running_signal = int(bool(data.get("runningSignal", 0)))
    alarm_signal = int(bool(data.get("alarmSignal", 0)))
    updated_at = datetime.now().isoformat(timespec="seconds")

    conn = get_db()
    conn.execute("""
        UPDATE machines
        SET status = ?,
            part_count = ?,
            running_signal = ?,
            alarm_signal = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        status,
        part_count,
        running_signal,
        alarm_signal,
        updated_at,
        machine_id
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "machine": machine_id,
        "status": status,
        "partCount": part_count,
        "updatedAt": updated_at
    })


@app.route("/api/machines", methods=["GET"])
def get_machines():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM machines ORDER BY id"
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    initialize_database()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
