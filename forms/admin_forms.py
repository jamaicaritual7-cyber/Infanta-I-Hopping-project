"""Forms for administrator-owned profile updates."""
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp
from flask_wtf import FlaskForm

from forms.auth_forms import validate_person_name, validate_phone_number, validate_common_password


class AdminProfileForm(FlaskForm):
    full_name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=150), validate_person_name])
    contact_number = StringField("Contact number", validators=[DataRequired(), Regexp(r"^09\d{9}$"), validate_phone_number])
    password = PasswordField(
        "New password (optional)",
        validators=[Optional(), Length(min=8, max=128), Regexp(r".*[A-Z].*"), Regexp(r".*[a-z].*"), Regexp(r".*\d.*"), validate_common_password],
    )
    confirm_password = PasswordField("Confirm new password", validators=[EqualTo("password", message="Passwords must match.")])
    submit = SubmitField("Save changes")
