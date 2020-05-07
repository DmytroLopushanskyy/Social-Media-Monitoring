"""
This module gives information about forms
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from db_connect import mongo


class RegistrationForm(FlaskForm):
    """
    This Form used in registration
    """
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        """
        Check username is not used earlier
        :param username: str
        :return: None
        """
        user = mongo.db.users.find_one({'name': username.data})
        if user:
            raise ValidationError('This username already taken. Please, choose another one')

    def validate_email(self, email):
        """
        Check email is not used earlier
        :param email: str
        :return: None
        """
        user = mongo.db.users.find_one({'email': email.data})

        if user:
            raise ValidationError('This email already taken. Please, choose another one')


class LoginForm(FlaskForm):
    """
    This Form used to Login User
    """
    username = StringField('Username',
                           validators=[DataRequired()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    submit = SubmitField('Login')
