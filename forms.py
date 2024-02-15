from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = StringField('Password', validators=[DataRequired()])
    confirmPassword = StringField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    password = StringField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')