from flask import Flask, request, render_template, flash, redirect, url_for, current_app, abort
from ..models import Applicant,Student, User
import string, random
from flask_sqlalchemy import SQLAlchemy
from forms import ApplicationForm, StudentLogin
from . import student
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from .. import db, bcrypt
import os
import secrets


def generate_password(stringLength=8):
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def save_picture(photo):
    random_name = secrets.token_hex(8)
    _, file_ext = os.path.splitext(photo.filename)
    file_name = random_name + file_ext
    file_path = os.path.join(current_app.root_path, 'static/profile', file_name)
    photo.save(file_path)
    return file_name

def save_doc(document):
    random_name = secrets.token_hex(8)
    _, file_ext = os.path.splitext(document.filename)
    file_name = random_name + file_ext
    file_path = os.path.join(current_app.root_path, 'static/documents', file_name)
    document.save(file_path)
    return file_name

@student.route('/apply', methods=['GET', 'POST'])
def apply():
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    form = ApplicationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                flash('There is already an account with that email.', 'warning')
                return redirect(url_for('student.apply'))
            stu = Student.query.filter_by(email=form.email.data).first()
            if stu is not None:
                flash('There is already a student with that email.', 'warning')
                return redirect(url_for('student.apply'))
            applicant = Applicant.query.filter_by(email=form.email.data).first()
            if applicant is not None:
                flash('You have already applied with that email.', 'warning')
                return redirect(url_for('student.apply'))
            if form.document.data:
                document = save_doc(form.document.data)
            student = Applicant(name=form.name.data, birthday=form.birthday.data, phone=form.phone.data, address=form.address.data, email=form.email.data, status=False, city=form.city.data, country=form.country.data, program=form.program.data, document=document)
            db.session.add(student)
            db.session.commit()
            flash('You application has been received!', 'success')
            return redirect(url_for('student.studentlogin'))
    return render_template('apply.html', form=form)

@student.route('/studentIndex', methods=['GET', 'POST'])
@login_required
def studentIndex():
    user_type = User.query.get(current_user.id)
    if user_type.type != "student":
        abort(403)
    return redirect(url_for('main.anouncement'))

@student.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    form = StudentLogin()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            print(user)
            if user is not None:
                print("hello")
                if bcrypt.check_password_hash(user.password, form.password.data) and user.type == "student":
                    login_user(user)
                    if form.checkbox.data is True:
                        login_user['remember'] = True
                    next = request.args.get('next')
                    if next is None or not next.startswith('/'):
                        next = url_for('student.studentIndex')
                    flash('You are logged in!', 'success')
                    return redirect(next)
            flash('Login failed! Please check username and password.', 'danger')
    return render_template('studentlogin.html', form=form)
