"""
BMI Calculator Web Application - Localhost Server (Flask)
Serves a modern web UI at http://localhost:5000 with REST API endpoints and SQLite integration.
"""

from flask import Flask, render_template, request, jsonify
import bmi_db
from bmi_cli import calculate_bmi, classify_bmi

app = Flask(__name__)

# Initialize database schema on startup
try:
    bmi_db.init_db()
except Exception as e:
    print(f"Warning initializing database: {e}")

@app.route("/")
def index():
    """Renders the main web application interface."""
    return render_template("index.html")

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """Calculates BMI and returns classification and WHO metadata."""
    data = request.get_json() or {}
    try:
        weight = float(data.get("weight", 0))
        height = float(data.get("height", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Weight and height must be valid numbers."}), 400

    if weight <= 0 or height <= 0:
        return jsonify({"error": "Weight and height must be greater than zero."}), 400

    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)

    return jsonify({
        "weight": weight,
        "height": height,
        "bmi": round(bmi, 2),
        "category": category
    })

@app.route("/api/users", methods=["GET"])
def api_users():
    """Returns a list of distinct users stored in the SQLite database."""
    try:
        users = bmi_db.get_users()
        return jsonify({"users": users})
    except bmi_db.DatabaseError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/records/<user_name>", methods=["GET"])
def api_get_records(user_name):
    """Retrieves all BMI records for a given user."""
    try:
        records = bmi_db.get_records(user_name)
        return jsonify({"user_name": user_name, "records": records})
    except bmi_db.DatabaseError as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/records", methods=["POST"])
def api_add_record():
    """Saves a new BMI record to the SQLite database."""
    data = request.get_json() or {}
    user_name = str(data.get("user_name", "")).strip()
    weight = data.get("weight")
    height = data.get("height")
    bmi = data.get("bmi")
    category = data.get("category")

    if not user_name:
        return jsonify({"error": "User name is required."}), 400

    if weight is None or height is None or bmi is None or not category:
        return jsonify({"error": "Incomplete record data."}), 400

    try:
        record_id = bmi_db.add_record(user_name, weight, height, bmi, category)
        return jsonify({"success": True, "record_id": record_id, "user_name": user_name})
    except bmi_db.DatabaseError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n=======================================================")
    print("  BMI Calculator Web Application is starting!")
    print("  Access in browser: http://localhost:5000")
    print("=======================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
