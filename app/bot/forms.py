from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class PechaSecretKeyForm(FlaskForm):
    secret_key = PasswordField("Pecha Secret Key", validators=[DataRequired()])
    submit = SubmitField("Submit")


class InvitationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Invitation")


class PechaIdForm(FlaskForm):
    pecha_id = StringField(
        "Pecha Id", validators=[DataRequired(), Length(min=1, max=7)]
    )
    submit = SubmitField("Join")
