import os
import sqlite3
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from database import create_database, DB_PATH

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

# Secret key
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-demo-secret-key-before-deployment"
)


# Database connection
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Login protection for pages
def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():

    # Redirect to home if already logged in
    if "username" in session:
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # Demo login credentials
        # Replace with database authentication for real users
        if username == "admin" and password == "Admin@123":
            session["username"] = username
            return redirect(url_for("home"))

        error = "Invalid username or password. Please try again."

    return render_template(
        "index.html",
        error=error,
        logged_in=False
    )


# Home page - District list
@app.route("/")
@login_required
def home():

    conn = get_connection()

    try:
        districts = conn.execute(
            "SELECT id, name FROM districts ORDER BY name"
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "index.html",
        districts=districts,
        logged_in=True
    )


# District details
@app.route("/district")
@login_required
def district_page():

    district_name = request.args.get("name", "").strip()

    if not district_name:
        return "Please select a district.", 400

    conn = get_connection()

    try:
        district = conn.execute(
            "SELECT * FROM districts WHERE name = ?",
            (district_name,)
        ).fetchone()

        services = conn.execute(
            """
            SELECT * FROM services
            WHERE district = ?
            ORDER BY category
            """,
            (district_name,)
        ).fetchall()
    finally:
        conn.close()

    if district is None:
        return "District not found.", 404

    return render_template(
        "district.html",
        district=district,
        services=services
    )


# Healthcare services
@app.route("/healthcare")
@login_required
def healthcare():

    conn = get_connection()

    try:
        services = conn.execute(
            """
            SELECT * FROM services
            WHERE category = 'Healthcare'
            ORDER BY district
            """
        ).fetchall()
    finally:
        conn.close()

    return render_template(
        "healthcare.html",
        services=services
    )


# Emergency information
@app.route("/emergency")
@login_required
def emergency():
    return render_template("emergency.html")


# Logout
@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


# Run application
if __name__ == "__main__":
    create_database()

    print("Rural Services Information App is running.")

    app.run(debug=True)
