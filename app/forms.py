from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField,PasswordField, SubmitField, SelectField, TextAreaField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError, Optional, NumberRange
from datetime import date
import re
from flask_wtf.file import MultipleFileField, FileField, FileAllowed


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
    
    address = StringField('Address (Door No, Street, Area)', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    
    
    
    
    
    
    submit = SubmitField('Register')

    

    # Custom email validation
    def validate_email(self, email):
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email.data):
            raise ValidationError("Enter a valid email address.")



class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional()])
    category = StringField('Category', validators=[DataRequired()])
    colour = StringField('Colour', validators=[Optional()])  # New colour field
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    manufacturer = StringField('Manufacturer', validators=[Optional()])
    country_of_origin = StringField('Country of Origin', validators=[Optional()])
    discount = FloatField('Discount', validators=[Optional()])
    images = MultipleFileField('Product Images', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Add Product')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

