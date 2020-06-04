from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class PechaSecretKeyForm(FlaskForm):
    secret_key = PasswordField("Pecha Secret Key", validators=[DataRequired()])
    submit = SubmitField("Submit")
