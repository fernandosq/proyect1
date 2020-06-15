import csv
import os
import base64

import flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, url_for, request, render_template, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, login_user, current_user, logout_user
from sqlalchemy.sql.functions import user
from werkzeug.urls import url_parse
from werkzeug.utils import redirect
from forms import *
from models import *





app = Flask(__name__)




#db config to me

app.config['SECRET_KEY']= base64.decodebytes(os.getenv("KEY").encode("utf-8"))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager(app)
login_manager.login_view = "login"
db.init_app(app)

# Check for environment variable

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db_session = scoped_session(sessionmaker(bind=engine))




#index_inicital
@app.route("/",methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/welcome",methods=["GET", "POST"])
def welcome():
    return render_template("welcome.html")

#manager
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))





@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        name=request.form.get("name")
        email= request.form.get("email")
        password = request.form.get("password")
        user=User(name=name,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        return render_template("welcome.html",)
    return render_template("signup_form.html",form=form)

   


#logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#login


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('welcome'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.get_by_email(email)
        if user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('welcome'))
    return render_template('login_form.html', title='Sign In', form=form)

#manager






if __name__== "__main__":
    with app.app_context():
        #main()
        app.run("127.0.0.1",port=5000,debug=True)






#api key 8fuK25fWwRuPi04o6cD1pA