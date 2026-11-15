"""Registration, login, and logout routes."""
from time import monotonic

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from extensions import db
from forms.auth_forms import LoginForm, RegistrationForm
from models.user import User
from services.email_service import send_verification_email
from services.otp_service import create_otp, verify_otp

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
_login_attempts = {}
LOGIN_LIMIT = 5
LOGIN_WINDOW_SECONDS = 300


def _login_is_limited(email):
    now = monotonic()
    attempts = [timestamp for timestamp in _login_attempts.get(email, []) if now - timestamp < LOGIN_WINDOW_SECONDS]
    _login_attempts[email] = attempts
    return len(attempts) >= LOGIN_LIMIT


def _record_failed_login(email):
    _login_attempts.setdefault(email, []).append(monotonic())


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if existing_user:
            if not existing_user.is_verified:
                session["verification_user_id"] = existing_user.id
                try:
                    code = create_otp(existing_user.id, db)
                    sent = send_verification_email(existing_user.email, code)
                except (ValueError, OSError, RuntimeError):
                    sent = False
                if sent:
                    flash("A new verification code was sent to your email.", "success")
                else:
                    flash("This account is waiting for email verification, but a new code could not be sent. Check the Flask terminal for the SMTP error.", "warning")
                return redirect(url_for("auth.verify_otp_route"))
            flash("An account with that email already exists.", "danger")
            return render_template("auth/register.html", form=form)
        user = User(
            full_name=form.full_name.data.strip(),
            email=form.email.data.lower().strip(),
            contact_number=form.contact_number.data.strip(),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("We could not create the account. Please check the details and try again.", "danger")
            return render_template("auth/register.html", form=form)
        session["verification_user_id"] = user.id
        try:
            code = create_otp(user.id, db)
            sent = send_verification_email(user.email, code)
        except (ValueError, OSError, RuntimeError):
            sent = False
        if not sent:
            flash("Account created, but the verification email could not be sent. Check SMTP settings and request a new code.", "warning")
        else:
            flash("A verification code was sent to your email.", "success")
        return redirect(url_for("auth.verify_otp_route"))
    if request.method == "POST" and not form.validate_on_submit():
        flash("Please correct the highlighted fields before submitting again.", "danger")
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if request.args.get("portal") == "admin" and current_user.role != "admin":
            abort(403)
        return redirect(url_for("home"))
    admin_portal = request.args.get("portal") == "admin"
    requested_next = request.args.get("next", "")
    if not admin_portal and requested_next.startswith("/") and not requested_next.startswith("//"):
        session["next_after_login"] = requested_next
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if _login_is_limited(email):
            flash("Too many failed login attempts. Please wait a few minutes and try again.", "warning")
            return render_template("auth/login.html", form=form)
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            _login_attempts.pop(email, None)
            if not user.is_verified:
                if admin_portal and user.role != "admin":
                    abort(403)
                session["verification_user_id"] = user.id
                flash("Please verify your email before logging in. Enter your code or resend it below.", "warning")
                return redirect(url_for("auth.verify_otp_route"))
            if admin_portal and user.role != "admin":
                abort(403)
            login_user(user)
            if admin_portal:
                return redirect(url_for("admin.dashboard"))
            next_url = session.pop("next_after_login", None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for("customer.my_bookings"))
        _record_failed_login(email)
        flash("Invalid email or password.", "danger")
    template = "auth/admin_login.html" if admin_portal else "auth/login.html"
    return render_template(template, form=form)


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp_route():
    user_id = session.get("verification_user_id")
    if not user_id:
        return redirect(url_for("auth.register"))
    user = db.session.get(User, user_id)
    if user is None:
        session.pop("verification_user_id", None)
        return redirect(url_for("auth.register"))
    if request.method == "POST":
        code = request.form.get("code", "")
        if len(code) == 6 and code.isdigit() and verify_otp(user.id, code, db):
            user.is_verified = True
            db.session.commit()
            session.pop("verification_user_id", None)
            flash("Your email has been verified. You can now log in.", "success")
            return redirect(url_for("auth.login"))
        flash("The code is invalid, expired, or has reached its attempt limit.", "danger")
    return render_template("auth/verify_otp.html")


@auth_bp.post("/resend-otp")
def resend_otp():
    user_id = session.get("verification_user_id")
    if not user_id:
        flash("Please start registration first.", "warning")
        return redirect(url_for("auth.register"))
    user = db.session.get(User, user_id)
    if user is None or user.is_verified:
        session.pop("verification_user_id", None)
        return redirect(url_for("auth.login"))
    try:
        code = create_otp(user.id, db)
        sent = send_verification_email(user.email, code)
    except (ValueError, OSError, RuntimeError):
        sent = False
    if sent:
        flash("A new verification code was sent to your email.", "success")
    else:
        flash("The new verification email could not be sent. Check the Flask terminal for the SMTP error.", "warning")
    return redirect(url_for("auth.verify_otp_route"))


@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

