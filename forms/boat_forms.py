"""Validated forms for administrator boat management."""

from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields import SelectChoice
from wtforms.validators import DataRequired, Length, NumberRange


class BoatForm(FlaskForm):
    name = StringField("Boat name", validators=[DataRequired(), Length(min=2, max=100)])
    fuel_type = StringField("Fuel type", validators=[DataRequired(), Length(max=50)])
    passenger_capacity = IntegerField(
        "Passenger capacity",
        validators=[DataRequired(), NumberRange(min=1, max=1000)],
    )
    description = TextAreaField("Description", validators=[Length(max=5000)])
    photograph_path = StringField("Photograph path", validators=[Length(max=255)])
    availability_status = SelectField(
        "Availability",
        choices=[
            SelectChoice("available", "Available"),
            SelectChoice("unavailable", "Unavailable"),
            SelectChoice("maintenance", "Maintenance"),
        ],
        validators=[DataRequired()],
    )
    is_active = BooleanField("Show this boat to customers", default=True)
    submit = SubmitField("Save boat")

