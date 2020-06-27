from flask import Flask, request, render_template, flash, redirect, url_for
import os
from app import create_app, db
from flask_migrate import Migrate


app = create_app(os.getenv('FLASK_CONFIG') or'default')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Applicant=Applicant, Admin=Admin, Student=Student, Post=Post)


def main():
    db.create_all()

with app.app_context():
    main()
