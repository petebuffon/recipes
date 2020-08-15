"""Define website forms."""
from flask_wtf import FlaskForm
from wtforms import Form, PasswordField, StringField, validators, FloatField, FieldList, TextAreaField, SelectField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, Optional
from wtforms.widgets import CheckboxInput


class Register(FlaskForm):
    """Registration form."""

    username = StringField("username")
    password = PasswordField("password", validators=[
        EqualTo("confirm", message="Password must be equal to confirm.")
    ])
    confirm = PasswordField('confirm')


class Login(FlaskForm):
    """Login form."""

    username = StringField("username")
    password = PasswordField("password")


class Recipe(FlaskForm):
    """Recipe form."""

    title = StringField("title")
    servings = FloatField("servings", [validators.optional()])
    source = StringField("source")
    notes = StringField("notes")
    ingredients = TextAreaField("ingredients")
    directions = TextAreaField("directions")


class Search(FlaskForm):
    """Search form."""

    search = StringField("search")
    select = SelectField("select", choices=["title", "category", "ingredient"], default="title")


class Import(FlaskForm):
    """Import form."""

    encoded = TextAreaField("encoded")
