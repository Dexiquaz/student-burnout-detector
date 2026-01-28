from flask import Flask, request, jsonify
from db import get_db_connection

app = Flask(__name__)

@app.route("/")
def home():
    return "Burnout Detector is running"

# Create a user
@app.route("/user", methods=["POST"])
def create_user():
    data = request.get_json()
    name = data.get("name")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    print("POST /user hit")


    return jsonify({"message": "User created"}), 201


# Log daily burnout data
@app.route("/log", methods=["POST"])
def log_data():
    data = request.get_json()

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO daily_logs (
            user_id, study_hours, sleep_hours, deadlines,
            stress_level, breaks, screen_time, physical_activity, log_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'))
    """, (
        data["user_id"],
        data["study_hours"],
        data["sleep_hours"],
        data["deadlines"],
        data["stress_level"],
        data["breaks"],
        data["screen_time"],
        data["physical_activity"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Daily log saved"}), 201

if __name__ == "__main__":
    app.run(debug=True)
