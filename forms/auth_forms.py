"""Authentication forms with server-side validation."""
import re

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError


def validate_person_name(_form, field):
    value = " ".join((field.data or "").split())
    if not value or not any(character.isalpha() for character in value):
        raise ValidationError("Name is required.")
    if any(not (character.isalpha() or character in " '-") for character in value):
        raise ValidationError("Name may contain letters, spaces, apostrophes, and hyphens only.")


def validate_project_email(_form, field):
    value = (field.data or "").strip()
    if any(character.isspace() for character in value):
        raise ValidationError("Email must not contain spaces.")
    if len(value) > 254 or value.count("@") != 1:
        raise ValidationError("Please enter a valid email address.")

    local_part, domain = value.rsplit("@", 1)
    if (
        not local_part
        or not domain
        or len(local_part) > 64
        or local_part.startswith(".")
        or local_part.endswith(".")
        or ".." in local_part
        or domain.startswith(".")
        or domain.endswith(".")
        or ".." in domain
        or "." not in domain
    ):
        raise ValidationError("Please enter a valid email address.")

    labels = domain.rstrip(".").split(".")
    if any(
        not label
        or len(label) > 63
        or label.startswith("-")
        or label.endswith("-")
        for label in labels
    ):
        raise ValidationError("Please enter a valid email domain.")


def validate_phone_number(_form, field):
    value = (field.data or "").strip()
    if re.search(r"(\d)\1{4}", value):
        raise ValidationError("Phone number cannot contain five identical consecutive digits.")


def validate_common_password(_form, field):
    common_passwords = {"password", "password123", "qwerty123", "12345678", "letmein123"}
    if field.data.lower() in common_passwords:
        raise ValidationError("Please choose a less common password.")


class RegistrationForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=150), validate_person_name])
    email = StringField(
        "Email address",
        validators=[DataRequired(), Length(max=254), validate_project_email, Email()],
    )
    contact_number = StringField(
        "Contact number",
        validators=[
            DataRequired(),
            Regexp(r"^09\d{9}$", message="Please enter an 11-digit Philippine mobile number starting with 09."),
            validate_phone_number,
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(r".*[A-Z].*", message="Password must contain an uppercase letter."),
            Regexp(r".*[a-z].*", message="Password must contain a lowercase letter."),
            Regexp(r".*\d.*", message="Password must contain a number."),
            validate_common_password,
        ],
    )
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField("Email address", validators=[DataRequired(), Length(max=254), validate_project_email, Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

