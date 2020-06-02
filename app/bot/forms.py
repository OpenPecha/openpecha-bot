from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class PechaSecretKeyForm(FlaskForm):
    secret_key = PasswordField(
        "Pecha Secret Key", validators=[DataRequired(), Length(min=32, max=32)]
    )
    submit = SubmitField("Submit")


class InvitationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Invitation")


class PechaIdForm(FlaskForm):
    pecha_id = StringField("Pecha Id")
    submit = SubmitField("Join")
