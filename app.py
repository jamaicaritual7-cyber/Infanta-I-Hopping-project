"""Application entry point for Infanta, I Hopping."""
import os
import re

import click
from flask import Flask, render_template
from sqlalchemy.exc import IntegrityError

from routes.boat_routes import boats_bp

from config import DevelopmentConfig, ProductionConfig
from extensions import csrf, db, login_manager
from models.user import User
from models.destination import Destination
from models.contact_inquiry import ContactInquiry
from models.contact_inquiry import ContactInquiry
from routes.auth_routes import auth_bp
from routes.booking_routes import booking_bp
from routes.customer_routes import customer_bp
from routes.admin_routes import admin_bp
from routes.main_routes import main_bp
from routes.destination_routes import destinations_bp
from services.destination_image_service import destination_image_catalog
from services.destination_content_service import destination_content_catalog


def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if config_class is ProductionConfig and app.config["SECRET_KEY"] == "change-this-development-secret":
        raise RuntimeError("Production requires a strong SECRET_KEY in the environment.")
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(boats_bp)
    app.register_blueprint(destinations_bp)

    @app.get("/")
    def home():
        featured_names = ("Dero Beach", "Sabangan Beach", "Baluti Island")
        featured_destinations = (
            Destination.query.filter(Destination.name.in_(featured_names), Destination.is_active.is_(True))
            .order_by(Destination.id)
            .all()
        )
        return render_template(
            "index.html",
            featured_destinations=featured_destinations,
            destination_image=destination_image_catalog.get,
            destination_content=destination_content_catalog.get,
        )

    @app.cli.command("sync-destination-content")
    def sync_destination_content():
        """Fill only missing destination descriptions from the reviewed content catalog."""
        record = destination_content_catalog.get("Pinagbanderahan Beach Resort")
        destination = Destination.query.filter_by(name="Pinagbanderahan Beach Resort").one_or_none()
        if destination is None:
            raise click.ClickException("Pinagbanderahan Beach Resort was not found; no database changes were made.")
        if not (destination.description or "").strip():
            destination.description = record.get("about")
            db.session.commit()
            click.echo(f"Updated description for destination id {destination.id}.")
        else:
            click.echo(f"Destination id {destination.id} already has a description; no overwrite performed.")

    @app.cli.command("create-first-admin")
    @click.option("--full-name", prompt="Administrator full name")
    @click.option("--email", prompt="Administrator email")
    @click.option("--contact-number", prompt="Administrator contact number")
    def create_first_admin(full_name, email, contact_number):
        """Create the first administrator through an explicit local confirmation."""
        full_name = " ".join(full_name.split())
        email = email.strip().lower()
        contact_number = contact_number.strip()

        if User.query.filter_by(role="admin").first():
            raise click.ClickException(
                "An administrator already exists. Refusing to create or promote another account."
            )
        if User.query.filter_by(email=email).first():
            raise click.ClickException(
                "That email already belongs to an account. Existing customers are never promoted by this command."
            )
        if (
            len(full_name) < 2
            or not any(character.isalpha() for character in full_name)
            or any(not (character.isalpha() or character in " '-") for character in full_name)
        ):
            raise click.ClickException("Enter a valid administrator name.")
        if not re.fullmatch(r"09\d{9}", contact_number):
            raise click.ClickException("Contact number must be an 11-digit Philippine mobile number starting with 09.")
        if not click.confirm("Create the first administrator account now?", default=False):
            click.echo("Cancelled. No account was created.")
            return

        password = click.prompt("Administrator password", hide_input=True, confirmation_prompt=True)
        common_passwords = {"password", "password123", "qwerty123", "12345678", "letmein123"}
        if (
            not 8 <= len(password) <= 128
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"\d", password)
            or password.lower() in common_passwords
        ):
            raise click.ClickException(
                "Password must be 8-128 characters with uppercase, lowercase, and a number, and must not be common."
            )

        admin = User(
            full_name=full_name,
            email=email,
            contact_number=contact_number,
            role="admin",
            is_verified=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise click.ClickException("The administrator could not be created because the account data conflicted.")
        click.echo(f"Administrator account created for {email}.")

    @app.cli.command("create-contact-inquiries-table")
    def create_contact_inquiries_table():
        """Create only the visitor inquiry table if it does not exist."""
        ContactInquiry.__table__.create(bind=db.engine, checkfirst=True)
        click.echo("contact_inquiries table is ready.")

    @app.cli.command("create-contact-inquiries-table")
    def create_contact_inquiries_table():
        """Create only the non-destructive visitor inquiry table if missing."""
        ContactInquiry.__table__.create(bind=db.engine, checkfirst=True)
        click.echo("contact_inquiries table is ready.")

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


_config_name = os.getenv("APP_ENV", "development").strip().lower()
app = create_app(ProductionConfig if _config_name == "production" else DevelopmentConfig)

if __name__ == "__main__":
    # Bind the single application instance to all local interfaces so the
    # browser's localhost and LAN URLs resolve to the same project.
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
    )

