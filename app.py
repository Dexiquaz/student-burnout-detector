def get_latest_log(user_id):
    conn = get_db_connection()
    log = conn.execute(
        """
        SELECT * FROM daily_logs
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()
    conn.close()
    return log

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


@app.route("/debug/latest/<int:user_id>")
def debug_latest(user_id):
    log = get_latest_log(user_id)

    if log is None:
        return {"message": "No data found for this user"}

    return dict(log)

def calculate_burnout_score(log):
    score = 0

    # 1. Study hours (mental load)
    if log["study_hours"] <= 4:
        score += 5
    elif log["study_hours"] <= 7:
        score += 10
    else:
        score += 20

    # 2. Sleep hours (recovery)
    if log["sleep_hours"] >= 7:
        score += 0
    elif log["sleep_hours"] >= 5:
        score += 10
    else:
        score += 20

    # 3. Deadlines (pressure)
    if log["deadlines"] <= 2:
        score += 5
    elif log["deadlines"] <= 5:
        score += 10
    else:
        score += 20

    # 4. Stress level (self-perception)
    score += log["stress_level"] * 5

    # 5. Breaks (micro-recovery)
    if log["breaks"] >= 3:
        score += 0
    elif log["breaks"] >= 1:
        score += 5
    else:
        score += 10

    # 6. Screen time (digital fatigue)
    if log["screen_time"] <= 2:
        score += 0
    elif log["screen_time"] <= 5:
        score += 5
    else:
        score += 10

    # 7. Physical activity (protective factor)
    if log["physical_activity"] == "high":
        score -= 10
    elif log["physical_activity"] == "medium":
        score -= 5

    return max(score, 0)

@app.route("/debug/score/<int:user_id>")
def debug_score(user_id):
    log = get_latest_log(user_id)

    if log is None:
        return {"message": "No data found"}

    score = calculate_burnout_score(log)
    return {
        "burnout_score": score
    }

@app.route("/analyze/<int:user_id>")
def analyze_burnout(user_id):
    log = get_latest_log(user_id)

    if log is None:
        return {"message": "No data found for this user"}, 404

    score = calculate_burnout_score(log)
    risk = classify_risk(score)

    save_burnout_result(user_id, score, risk)

    return {
        "user_id": user_id,
        "burnout_score": score,
        "risk_level": risk
    }


def classify_risk(score):
    if score <= 30:
        return "Low"
    elif score <= 60:
        return "Medium"
    else:
        return "High"

def save_burnout_result(user_id, score, risk):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO burnout_scores (user_id, score, risk_level) VALUES (?, ?, ?)",
        (user_id, score, risk)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run(debug=True)
