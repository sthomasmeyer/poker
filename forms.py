# Import [FlaskForm], a Flask-specific subclass of WTForms [Form] base class.
from flask_wtf import FlaskForm

# Import desired basic fields (i.e., BooleanField, IntegerField) from [wtforms].
# These generally represent scalar data types w/ single values, and...
# refer to a single input from the form. For example, there is a [DecimalField()]...
# w/ parameters related to # of places, rounding (up or down), and number format.
from wtforms import StringField, EmailField, PasswordField

# Import desired validators (i.e., URL, InputRequired) from [wtforms.validators].
# Validators in WTForms are designd to ensure a given input fulfills some criterion...
# For example, there is a [Regexp()] validator that compares the value of the field...
# against a user-provided regexp.
from wtforms.validators import InputRequired, Email, Length


class UserLoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class CreateAccountForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(max=24)])
    email = EmailField(
        "Email", validators=[InputRequired(), Email(check_deliverability=True)]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8)])
