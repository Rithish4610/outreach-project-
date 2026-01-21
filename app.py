from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route("/")
def token_generator():
    return render_template("token_generator.html")

@app.route("/generate", methods=["POST"])
def generate_token():
    name = request.form["name"]
    mobile = request.form["mobile"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT MAX(token_number) FROM tokens")
    last_token = cursor.fetchone()[0]

    token_number = 1 if last_token is None else last_token + 1

    cursor.execute(
        "INSERT INTO tokens (token_number, name, mobile, status) VALUES (?, ?, ?, ?)",
        (token_number, name, mobile, "waiting")
    )

    conn.commit()
    conn.close()

    return f"Token Generated Successfully. Your Token Number is {token_number}"

@app.route("/doctor")
def doctor():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tokens WHERE status='waiting'")
    tokens = cursor.fetchall()

    conn.close()
    return render_template("doctor.html", tokens=tokens)

@app.route("/next", methods=["POST"])
def next_patient():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tokens WHERE status='waiting' ORDER BY token_number LIMIT 1")
    current = cursor.fetchone()

    if current:
        cursor.execute("UPDATE tokens SET status='done' WHERE id=?", (current[0],))

    conn.commit()
    conn.close()

    return redirect("/doctor")

@app.route("/patient")
def patient_login():
    return render_template("patient_login.html")

@app.route("/status", methods=["POST"])
def status():
    token = request.form["token"]
    mobile4 = request.form["mobile4"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT token_number FROM tokens WHERE status='waiting' ORDER BY token_number LIMIT 1")
    current_token = cursor.fetchone()

    cursor.execute(
        "SELECT token_number, mobile FROM tokens WHERE token_number=?",
        (token,)
    )
    patient = cursor.fetchone()
    conn.close()

    if not patient or not patient[1].endswith(mobile4):
        return "Invalid details"

    if current_token:
        wait_time = (int(token) - current_token[0]) * 5
    else:
        wait_time = 0

    return render_template(
        "patient_status.html",
        current=current_token[0] if current_token else None,
        your=token,
        time=wait_time
    )

if __name__ == "__main__":
    # Database creation logic (run once)
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_number INTEGER,
        name TEXT,
        mobile TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("Database created successfully")
    app.run(debug=True)
