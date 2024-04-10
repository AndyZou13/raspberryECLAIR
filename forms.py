from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, EqualTo, StopValidation
from datetime import datetime

def checkTime(form, field):
    now = datetime.now()
    print(now)
    print(field.data)
    if field.data < now:
        field.errors[:] = []
        raise StopValidation('This field is required.')
    
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
    datum = DateTimeLocalField('Datum', validators=[DataRequired(), checkTime])
    submit3 = SubmitField('Tier 3 \n 48 amps max output \n 12kW of power per hour')
    submit2 = SubmitField('Tier 2 \n 40 amps max output \n 10kW of power per hour')
    submit1 = SubmitField('Tier 1 \n 32 amps max output \n 8kW of power per hour')