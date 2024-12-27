from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError
from datetime import date
import re

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters.")
    ])
    
    email = StringField('Email', validators=[DataRequired()])
    
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long.")
    ])
    
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match.")
    ])
    
    role = SelectField('Role', choices=[
        ('customer', 'Customer'),
        ('delivery', 'Delivery')
    ], validators=[DataRequired()])
    
    contact = StringField('Contact', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message="Contact number must be 10 digits.")
    ])
    
    location = StringField('Location', validators=[DataRequired()])
    
    dob = DateField('Date of Birth', validators=[
        DataRequired(message="Please enter a valid date in the format YYYY-MM-DD.")
    ])
    
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Register')

    # Custom validator for the date of birth
    def validate_dob(self, dob):
        if dob.data > date.today():
            raise ValidationError("Date of Birth cannot be in the future.")

    # Custom email validation
    def validate_email(self, email):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email.data):
            raise ValidationError("Enter a valid email address.")























class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

