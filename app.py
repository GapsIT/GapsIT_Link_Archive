from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
from config import Config
from models import db, Link
from auth_utils import login_required, admin_required, verify_token_with_auth_system

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    """Home page - redirect to login or dashboard"""
    if "access_token" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))


@app.route("/login")
def login_page():
    """Login page"""
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def login():
    """Login via core auth system"""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    try:
        # Authenticate with core auth system
        auth_url = app.config["AUTH_SYSTEM_URL"]
        response = requests.post(
            f"{auth_url}/api/auth/login/",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            data = response.json()
            # Store tokens in session
            session["access_token"] = data["access"]
            session["refresh_token"] = data.get("refresh")
            session["username"] = username

            return jsonify({"success": True, "message": "Login successful"})
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/logout")
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard - shows links based on user position"""
    employee_info = request.employee_info
    return render_template("dashboard.html", employee=employee_info)


@app.route("/admin")
@admin_required
def admin_panel():
    """Admin panel for managing links"""
    employee_info = request.employee_info
    return render_template("admin.html", employee=employee_info)


@app.route("/api/links", methods=["GET"])
@login_required
def get_links():
    """Get links for current user's position"""
    employee_info = request.employee_info
    user_position = employee_info.get("position")

    # Get all links and filter by position
    all_links = Link.query.order_by(Link.created_at.desc()).all()

    # Filter links that include user's position
    links = [link for link in all_links if link.has_position(user_position)]

    return jsonify(
        {"links": [link.to_dict() for link in links], "position": user_position}
    )


@app.route("/api/admin/links", methods=["GET"])
@admin_required
def get_all_links():
    """Get all links (admin only)"""
    links = Link.query.order_by(Link.created_at.desc()).all()
    return jsonify({"links": [link.to_dict() for link in links]})


@app.route("/api/admin/links", methods=["POST"])
@admin_required
def create_link():
    """Create new link (admin only)"""
    data = request.json
    employee_info = request.employee_info

    title = data.get("title")
    url = data.get("url")
    description = data.get("description", "")
    positions = data.get("positions", [])  # Changed: Now accepts list

    if not title or not url or not positions:
        return jsonify(
            {"error": "Title, URL, and at least one position are required"}
        ), 400

    link = Link(
        title=title,
        url=url,
        description=description,
        created_by=employee_info.get("user", {}).get("username"),
    )
    link.set_positions_list(positions)  # Set positions from list

    db.session.add(link)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Link created successfully",
            "link": link.to_dict(),
        }
    ), 201


@app.route("/api/admin/links/<int:link_id>", methods=["PUT"])
@admin_required
def update_link(link_id):
    """Update link (admin only)"""
    link = Link.query.get_or_404(link_id)
    data = request.json

    link.title = data.get("title", link.title)
    link.url = data.get("url", link.url)
    link.description = data.get("description", link.description)

    # Update positions if provided
    if "positions" in data:
        positions = data.get("positions", [])
        if positions:
            link.set_positions_list(positions)

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "message": "Link updated successfully",
            "link": link.to_dict(),
        }
    )


@app.route("/api/admin/links/<int:link_id>", methods=["DELETE"])
@admin_required
def delete_link(link_id):
    """Delete link (admin only)"""
    link = Link.query.get_or_404(link_id)
    db.session.delete(link)
    db.session.commit()

    return jsonify({"success": True, "message": "Link deleted successfully"})


@app.route("/api/positions", methods=["GET"])
@login_required  # Changed: Allow all authenticated users to see positions
def get_positions():
    """Get all unique positions (for dropdown in admin panel)"""
    # Get unique positions from core auth system
    try:
        auth_url = app.config["AUTH_SYSTEM_URL"]
        token = session.get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(f"{auth_url}/api/employees/", headers=headers)

        if response.status_code == 200:
            employees = response.json().get("results", [])
            positions = list(
                set(emp.get("position") for emp in employees if emp.get("position"))
            )
            return jsonify({"positions": sorted(positions)})

        return jsonify({"positions": []})
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return jsonify({"positions": []})


@app.route("/api/debug/me", methods=["GET"])
@login_required
def debug_me():
    """Debug endpoint to check employee info"""
    employee_info = request.employee_info
    return jsonify(
        {
            "employee_info": employee_info,
            "is_admin": employee_info.get("is_admin", False),
            "role": employee_info.get("role", "N/A"),
            "position": employee_info.get("position", "N/A"),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
