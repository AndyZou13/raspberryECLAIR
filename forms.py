from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateTimeLocalField
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
    
class BookingForm(FlaskForm):
    datum = DateTimeLocalField('Datum', validators=[DataRequired()])
    submit3 = SubmitField('Tier 3 \n 48 amps max output \n 11.5kW of power per hour')
    submit2 = SubmitField('Tier 2 \n 40 amps max output \n 9.6kW of power per hour')
    submit1 = SubmitField('Tier 1 \n 32 amps max output \n 7.7kW of power per hour')