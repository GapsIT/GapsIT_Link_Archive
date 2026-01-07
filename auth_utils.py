import requests
import jwt
from functools import wraps
from flask import redirect, request, jsonify, session, current_app, url_for


def verify_token_with_auth_system(token):
    """Verify token and get employee info from core auth system"""
    try:
        auth_url = current_app.config["AUTH_SYSTEM_URL"]
        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(f"{auth_url}/api/employees/me/", headers=headers)

        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


def decode_jwt_token(token):
    """Decode JWT token to get claims (role, position, etc.)"""
    try:
        # Decode without verification for getting claims
        # In production, you should verify with public key
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None


def verify_admin_status(user_id):
    """Verify if user is admin via API key"""
    try:
        auth_url = current_app.config["AUTH_SYSTEM_URL"]
        api_key = current_app.config["AUTH_API_KEY"]

        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        data = {"user_id": user_id}

        response = requests.post(
            f"{auth_url}/api/employees/verify_admin/", headers=headers, json=data
        )

        if response.status_code == 200:
            return response.json().get("is_admin", False)
        return False
    except Exception as e:
        print(f"Error verifying admin: {e}")
        return False


def login_required(f):
    """Decorator to require login"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        # Verify token is still valid
        employee_info = verify_token_with_auth_system(token)
        if not employee_info:
            session.clear()
            return jsonify({"error": "Invalid or expired token"}), 401

        # Store employee info in request context
        request.employee_info = employee_info
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("access_token")
        if not token:
            return redirect(url_for("login_page"))

        # Verify token and get employee info
        employee_info = verify_token_with_auth_system(token)
        if not employee_info:
            session.clear()
            return redirect(url_for("login_page"))

        # Check if admin
        is_admin = employee_info.get("is_admin", False)

        # Debug logging
        print(
            f"Admin check - User: {employee_info.get('name')}, is_admin: {is_admin}, role: {employee_info.get('role')}"
        )

        if not is_admin:
            # For HTML routes, redirect to dashboard
            if request.path.startswith("/admin"):
                from flask import flash

                return redirect(url_for("dashboard"))
            # For API routes, return JSON error
            return jsonify({"error": "Admin privileges required"}), 403

        request.employee_info = employee_info
        return f(*args, **kwargs)

    return decorated_function
