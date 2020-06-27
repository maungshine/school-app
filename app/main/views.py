from flask import Flask, request, render_template, flash, redirect, url_for, abort, current_app
from ..models import Applicant, Admin, Student, User, Post
import os
import random
import string
from flask_mail import Message
from flask_sqlalchemy import SQLAlchemy
from forms import SearchForm, RemoveForm, UpdateForm, AdminLogin, AdminRegister, ApplicationForm, StudentLogin, PostForm, RequestPasswordResetForm, PasswordResetForm, AdminUpdateForm, ChangePasswordForm
from . import main
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from email_validator import EmailNotValidError,validate_email
from .. import db, bcrypt, mail
from ..student.views import save_picture

def generate_password(stringLength=8):
    """Generate password containg alphanumeric characters"""
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))

def send_reset_email(user, type):
    """send an email containing reset password link to the email address of user object
    user is an instance of User class"""
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="noreply@demo.com", recipients=[user.email])
    msg.body = f"""Reset link:
{url_for('main.resetPassword',type=type, token=token, _external=True)}
"""
    mail.send(msg)

@main.route('/')
@login_required
def index():
    user_type  = User.query.get(current_user.id)
    if user_type.type == "student":
        abort(404)
    page = request.args.get('page', 1, type=int)
    students = Student.query.paginate(page=page, per_page=5)
    return render_template('index.html', students=students)

@main.route('/applicant')
@login_required
def applicant():
    user_type = User.query.get(current_user.id)
    if user_type.type != "admin":
        abort(403)
    page = request.args.get('page', 1, type=int)
    applicants = Applicant.query.order_by(Applicant.id.desc()).paginate(page=page, per_page=5)
    return render_template('applicant.html', applicants=applicants)

@main.route('/find', methods=['GET', 'POST'])
@login_required
def find():
    user_type = User.query.get(current_user.id)
    if user_type.type == "student":
        abort(403)
    form = SearchForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            #search for students
            if form.option1.data == "student":
                if form.option.data == "name":
                    student_name = form.name.data
                    check = Student.query.filter_by(name=student_name).first()
                    if check is None:
                        flash('There is no sutudent with that {}'.format(form.option.data), 'info')
                        return redirect(url_for('main.find'))
                    students = Student.query.filter_by(name=student_name)
                    return render_template('result.html', students=students, type="student")
                student_id = form.name.data
                checkId = Student.query.filter_by(studentid=student_id).first()
                if checkId is None:
                    flash('There is no sutudent with that {}.'.format(form.option.data), 'info')
                    return redirect(url_for('main.find'))
                students = Student.query.filter_by(studentid=student_id)
                return render_template('result.html', students=students, type="student")
            #search for applicants
            if form.option.data == "name":
                student_name = form.name.data
                check = Applicant.query.filter_by(name=student_name).first()
                if check is None:
                    flash('There is no applicant with that {}'.format(form.option.data))
                    return redirect(url_for('main.find'))
                students = Applicant.query.filter_by(name=student_name)
                return render_template('result.html', students=students, type="applicant")
            student_id = form.name.data
            checkId = Applicant.query.filter_by(id=student_id).first()
            if checkId is None:
                flash('There is no sutudent with that {}.'.format(form.option.data), 'info')
                return redirect(url_for('main.find'))
            students = Applicant.query.filter_by(id=student_id)
            return render_template('result.html', students=students, type="applicant")

    return render_template('find.html', form=form)

@main.route('/profile/<type>/<int:id>', methods=['GET'])
@login_required
def profile(type,id):
    file_path = os.path.join(current_app.root_path, 'static/documents')
    if type == 'admin':
        admin = Admin.query.filter_by(user_id=id).first()
        if not admin or current_user.type == 'student' or current_user.id != admin.user_id:
            abort(403)
        return render_template('profile.html', admin=admin, type=type, id=admin.adminID, file_path=file_path)
    if current_user.type == "admin":
        student = Student.query.get_or_404(id)
        return render_template('profile.html', student=student, type=type, file_path=file_path)

    student = Student.query.filter_by(user_id=id).first()
    if current_user.id != student.user_id:
        abort(403)
    return render_template('profile.html', student=student, type=type, id=student.studentid, file_path=file_path)


@main.route('/remove/<type>/<int:id>', methods=['POST'])
@login_required
def remove(type,id):
    print('hi')
    user_type = User.query.get(current_user.id)
    if user_type.type != "admin":
        abort(403)
    if type == 'student':
        print('hi')
        student = Student.query.get(id)
        db.session.delete(student)
        db.session.commit()
        user = User.query.filter_by(email=student.email).first()
        db.session.delete(user)
        db.session.commit()
        flash(f'The {student.name} has been removed.', 'success')
        return redirect(url_for('main.index'))
    if type == 'admin':

        admin = Admin.query.get(id)
        db.session.delete(admin)
        db.session.commit()
        user = User.query.filter_by(email=admin.email).first()
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash(f'The {admin.username} has been removed.', 'success')
        return redirect(url_for('main.adminlogin'))
    if type == 'applicant':
        applicant = Applicant.query.get(id)
        db.session.delete(applicant)
        db.session.commit()
        flash(f'The {applicant.name} has been removed.', 'success')
        return redirect(url_for('main.applicant'))


@main.route('/update/<type>/<int:id>', methods=['GET', 'POST'])
@login_required
def update(type,id):
    form = UpdateForm()
    file_path = os.path.join(current_app.root_path, 'static/documents')
    if type == 'applicant':
        student = Applicant.query.get_or_404(id)

        if request.method == 'POST':
            if form.validate_on_submit():
                student.name = form.name.data
                student.email = form.email.data
                student.birthday = form.birthday.data
                student.phone = form.phone.data
                student.address = form.address.data
                student.city = form.city.data
                student.country = form.country.data
                student.program = form.program.data
                db.session.commit()
                flash('The applicant information has been updated.', 'success')
                return redirect(url_for('main.applicant'))
    if type == 'student':
        student = Student.query.get_or_404(id)
        if request.method == 'POST':

            if form.validate_on_submit():

                if form.profile.data:
                    profile_pic = save_picture(form.profile.data)
                    student.image = profile_pic

                user = User.query.get(student.user_id)
                user.name = form.name.data
                user.email = form.email.data
                student.name = form.name.data
                student.email = form.email.data
                student.birthday = form.birthday.data
                student.phone = form.phone.data
                student.address = form.address.data
                student.city = form.city.data
                student.country = form.country.data
                student.program = form.program.data
                db.session.commit()
                flash('The student information has been updated.', 'success')
                if current_user.type == 'admin':
                    return redirect(url_for('main.profile', type=type, id=student.studentid))
                return redirect(url_for('main.profile', type=type, id=current_user.id))
    if type == 'admin':
        adminform = AdminUpdateForm()
        admin = Admin.query.get_or_404(id)

        if request.method == 'POST':
            print('admin again')
            if adminform.validate_on_submit():
                print('admin again and again')
                if adminform.profile.data:
                    profile_pic = save_picture(adminform.profile.data)
                    admin.image = profile_pic

                user = User.query.get(admin.user_id)
                user.username = adminform.username.data
                user.email = adminform.email.data
                admin.username = adminform.username.data
                admin.email = adminform.email.data
                admin.school = adminform.school.data
                db.session.commit()
                flash('The student information has been updated.', 'success')
                return redirect(url_for('main.profile', type=type, id=id))


        adminform.username.data = admin.username
        adminform.email.data = admin.email
        adminform.school.data = admin.school
        return render_template('update.html', form=adminform, id=id, type=type, file_path=file_path, admin=admin)
    form.name.data = student.name
    if type != 'applicant':
        form.profile.data = student.image
    form.email.data = student.email
    form.birthday.data = student.birthday
    form.phone.data = student.phone
    form.address.data = student.address
    form.city.data = student.city
    form.country.data = student.country
    form.program.data = student.program
    return render_template('update.html', form=form, id=id, type=type, file_path=file_path, student=student)

@main.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    form = AdminLogin()
    if request.method == 'POST':
        try:
            valid = validate_email(form.email.data)
            email = valid.email
        except EmailNotValidError as e:
            flash('Invalid email!', 'danger')
            return redirect(url_for('main.adminlogin'))
        admin = User.query.filter_by(email=form.email.data).first()
        if admin is None:
            flash('Login failed! Please check username and password.', 'danger')
            return redirect(url_for('main.adminlogin'))
        if bcrypt.check_password_hash(admin.password, form.password.data) and admin.email is not None and admin.type == "admin":
            print(admin)
            login_user(admin)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            flash('You have been logged in!', 'success')
            return redirect(next)
        else:
            flash('Login failed! Check email and password agian.', 'danger')
            return redirect(url_for('main.adminlogin'))
    return render_template('adminlogin.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    form = AdminRegister()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None:
                flash('There is already an account with that email.', 'warning')
                return redirect(url_for('main.register'))
            pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(name=form.username.data, email=form.email.data, password=pw_hash, type="admin")
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(email=form.email.data).first()
            admin = Admin(school=form.school.data, username=form.username.data, email=form.email.data, user_id=user.id )
            db.session.add(admin)
            db.session.commit()
            flash('You have been registered!', 'success')
            return redirect(url_for('main.adminlogin'))
    return render_template('register.html', form=form)

@main.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    user = User.query.get(int(current_user.id))
    logout_user()
    flash('You are logged out!', 'success')
    if user.type == "admin":
        return redirect(url_for('main.adminlogin'))
    return redirect(url_for('student.studentlogin'))

@main.route('/addstudent/<int:id>', methods=['POST'])
@login_required
def addstudent(id):
    user_type = User.query.get(current_user.id)
    if user_type.type != "admin":
        abort(403)
    student = Applicant.query.get(id)
    userToCheck = User.query.filter_by(email=student.email).first()
    studentToCheck = Student.query.filter_by(email=student.email).first()
    if studentToCheck is not None and userToCheck is not None:
        flash(f'{studentToCheck.name} is already our student.', 'danger')
        return redirect(url_for('main.applicant'))
    password = generate_password()
    print("Password: ",password)
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(name=student.name, email=student.email, password=pw_hash, type="student")
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(email=student.email).first()
    studentToAdd = Student(name=student.name, birthday=student.birthday, phone=student.phone, address=student.address, email=student.email, user_id=user.id, city=student.city, country=student.country, program=student.program, document=student.document)
    db.session.add(studentToAdd)
    db.session.commit()
    student.status = True
    db.session.commit()
    msg = Message("Congratulations", sender="noreply@demo.com", recipients=[student.email])
    msg.body = f"""You have been accepted!
Your username and password for student account is given below.
        Username: {student.email}
        Password: {password}
You can login through this link:
{url_for('student.studentlogin', _external=True)}"""
    try:
        mail.send(msg)
        flash(f'{student.name} has been added to the accpeted student list!', 'success')
        return redirect(url_for('main.applicant'))
    except:
        flash(f'{student.name} has been added to the accpeted student list but email cannot be sent.', 'warning')
        return redirect(url_for('main.applicant'))

@main.route('/anouncement', methods=['GET', 'POST'])
@login_required
def anouncement():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=5)
    for post in posts.items:
        print(post.date)
    return render_template('anouncement.html', posts=posts)

@main.route('/createpost', methods=['GET', 'POST'])
@login_required
def createpost():
    if current_user.type != 'admin':
        abort(403)
    form = PostForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            title = form.title.data
            body = form.post.data
            post = Post(title=title, post=body, user_id=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Your anouncement has been posted.", 'success')
            return redirect(url_for('main.anouncement'))
    return render_template('createpost.html', form=form)

@main.route('/editpost/<int:id>', methods=['GET', 'POST'])
@login_required
def editpost(id):
    if current_user.type != 'admin':
        abort(403)
    form = PostForm()
    post = Post.query.get_or_404(id)
    if request.method == 'POST':
        if form.validate_on_submit:
            post.title = form.title.data
            post.post = form.post.data
            db.session.commit()
            flash(f"Your post has been edited.", "success")
            return redirect(url_for('main.anouncement'))
    form.title.data = post.title
    form.post.data = post.post
    return render_template('editpost.html', form=form, postid=id)

@main.route('/deletepost/<int:id>', methods=['POST'])
@login_required
def deletepost(id):
    if current_user.type != 'admin':
        abort(403)
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted.", 'success')
    return redirect(url_for('main.anouncement'))

@main.route('/pwResetRequest/<type>', methods=['GET', 'POST'])
def pwResetRequest(type):
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    form =  RequestPasswordResetForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('There is no account with that email', 'danger')
                return redirect(url_for('main.pwResetRequest', type=type))
            send_reset_email(user, type)
            flash('Password reset email has been sent to your email.', 'success')
            if user.type == 'admin':
                return redirect(url_for('main.adminlogin'))
            return redirect(url_for('student.studentlogin'))
    return render_template('pw_reset_request.html', form=form, type=type)


@main.route('/resetPassword/<type>/<token>', methods=['GET','POST'])
def resetPassword(token,type):
    if current_user.is_authenticated:
        if current_user.type == 'admin':
            return redirect(url_for('main.index'))
        return redirect(url_for('student.studentIndex'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token', 'warning')
        return redirect(url_for('main.pwResetRequest'))
    form = PasswordResetForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            pw_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = pw_hash
            db.session.commit()
            flash('Your account password has been updated.', 'success')
            if user.type == 'admin':
                return redirect(url_for('main.adminlogin'))
            return redirect(url_for('student.studentlogin'))
    return render_template('reset_password.html', form=form, type=type)

@main.route('/changepw', methods=['GET', 'POST'])
@login_required
def changepw():
    form = ChangePasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            user = User.query.get(current_user.id)
            if bcrypt.check_password_hash(user.password, form.old_password.data):
                user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
                db.session.commit()
                flash('Password has been changed.', 'success')
                return redirect(url_for('main.profile', id=user.id, type=user.type))
            flash('Wrong old password!', 'danger')
    return render_template('changepw.html', form=form)
