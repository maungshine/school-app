from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, IntegerField, PasswordField, BooleanField, SelectField, DateField,
                    TextField, TextAreaField)
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed

class ApplicationForm(FlaskForm):
    name = StringField('Student Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    program = SelectField('Choose program', choices=[('Web Development', 'Web Development'), ('Mobile App Developmet', 'Mobile App Developmet')], validators=[DataRequired()])
    document = FileField('Upload Documents', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Apply')

class SearchForm(FlaskForm):
    name = StringField('Name or ID', validators=[DataRequired()])
    option = SelectField('Search by: ',choices=[('name','Name'),('id', 'ID')], validators=[DataRequired()])
    option1 = SelectField('Student or Applicant: ',choices=[('student','Student'),('applicant', 'Applicant')], validators=[DataRequired()])
    submit = SubmitField('Search')

class RemoveForm(FlaskForm):
    id = IntegerField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Remove')

class UpdateForm(FlaskForm):
    name = StringField('Student Name', validators=[DataRequired()])
    profile = FileField('Upload Profile', validators=[FileAllowed(['jpg','png'])])
    email = StringField('Email', validators=[DataRequired(), Email()])
    birthday = DateField('Birthday', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    program = StringField('Choose program', validators=[DataRequired()])
    submit = SubmitField('Submit')

class AdminUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    profile = FileField('Upload Profile', validators=[FileAllowed(['jpg','png'])])
    email = StringField('Email', validators=[DataRequired(), Email()])
    school = StringField('School', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AdminRegister(FlaskForm):
    school = StringField('School Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8) ])
    pw_confirmation = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

class AdminLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    checkbox = BooleanField('Remember me')
    submit = SubmitField('Login')

class StudentLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passowrd', validators=[DataRequired()])
    checkbox = BooleanField('Remember me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = TextField('Title', validators=[DataRequired()])
    post = TextAreaField('What is it about?')
    submit = SubmitField('Post')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8) ])
    pw_confirmation = PasswordField('Confirm Password', validators=[EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired(), Length(min=8) ])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8) ])
    submit = SubmitField('Submit Changes')
