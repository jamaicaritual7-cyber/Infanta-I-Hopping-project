"""Forms used for customer booking requests."""

from datetime import datetime, timedelta, timezone

from flask_wtf import FlaskForm

from wtforms import DateField, IntegerField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


PH_TIMEZONE = timezone(timedelta(hours=8), name="Asia/Manila")


class BookingForm(FlaskForm):
    destination_id = SelectField("Destination", coerce=int, validators=[DataRequired()])
    boat_id = SelectField("Boat", coerce=int, validators=[DataRequired()])
    trip_date = DateField(
        "Trip date",
        validators=[DataRequired()],
        format="%Y-%m-%d",
        default=lambda: datetime.now(PH_TIMEZONE).date(),
        render_kw={"type": "text", "autocomplete": "off", "placeholder": "MM/DD/YYYY"},
    )
    passenger_count = IntegerField(
        "Number of passengers",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
    )
    special_request = TextAreaField("Additional request", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Submit booking request")

