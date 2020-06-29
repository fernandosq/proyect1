import csv
import os
import base64
import requests
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

#manager
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


#index_inicital
@app.route("/",methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/welcome",methods=["GET", "POST"])
def welcome():

    option = request.form.get('options')
    value_to_search = "%"+str(request.form.get("buscador"))+"%"
    search_result = []

    if option == "ISBN":
        #search_result =book.query.filter_by(isbn=value_to_search).all()
        search_result = db_session.execute(f"SELECT * FROM books WHERE isbn LIKE '{value_to_search}'").fetchall()
    if option == "TITLE":
        #search_result =book.query.filter_by(title=value_to_search).all()
        search_result = db_session.execute(f"SELECT * FROM books WHERE title LIKE '{value_to_search}'").fetchall()

    if option == "AUTHOR":
        #search_result =book.query.filter_by(author = value_to_search).all()
        search_result = db_session.execute(f"SELECT * FROM books WHERE author LIKE '{value_to_search}'").fetchall()

    if len(search_result) == 0:
        return render_template("welcome.html",form=SearchForm())
    return render_template("results.html",search_result=search_result)

@app.route("/search/<int:isbn>")
def book(isbn):
    book_data=db_session.execute(f"SELECT * FROM books WHERE isbn ='{isbn}'").fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8fuK25fWwRuPi04o6cD1pA", "isbns": book_data["isbn"]})
    good_read_data=res.json()
    good_read_data_average_data=good_read_data["books"][0]["average_rating"]
    good_read_data_ratings_count = good_read_data["books"][0]["ratings_count"]
    return render_template("book.html",good_read_data_average_data=good_read_data_average_data,good_read_data_ratings_count=good_read_data_ratings_count)





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
        return render_template("welcome.html",form=SearchForm())
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