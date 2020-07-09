import csv
import os
import base64
import requests
import flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, session, url_for, request, render_template, flash, jsonify
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

@login_manager.user_loader
def load_user(id):
    return User.get_by_id(int(id))
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

@app.route("/search/<isbn>", methods=['GET',"POST"])
def book(isbn):
    """this def explain all it"""
    book_data=db_session.execute(f"SELECT * FROM books WHERE isbn ='{isbn}'").fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "8fuK25fWwRuPi04o6cD1pA", "isbns": book_data["isbn"]})
    good_read_data=res.json()
    good_read_data_average_data=good_read_data["books"][0]["average_rating"]
    good_read_data_ratings_count = good_read_data["books"][0]["ratings_count"]
    #show_reviews_info
    review_text=db_session.execute(f"SELECT review_text FROM reviews_table WHERE id_review ='{book_data.isbn}'").fetchall()
    review_count = db.session.execute(f"SELECT review_text FROM reviews_table WHERE id_review ='{book_data.isbn}'").rowcount
    average_score = db.session.execute(f"SELECT review_score FROM reviews_table WHERE id_review ='{book_data.isbn}'").fetchone()



    #form_create_review
    form = ReviewsForm()
    if form.submit:
        review_tex = request.form.get("review_tex")
        review_score = request.form.get("review_score")
        review = Review(review_score=review_score,review_text=review_tex,id_review=book_data.isbn)
        db.session.add(review)
        db.session.commit()


    return render_template("book.html", good_read_data_average_data=good_read_data_average_data,
                           good_read_data_ratings_count=good_read_data_ratings_count,
                           book_data=book_data,
                           form=form,
                           review_text=review_text,
                           review_count=review_count,
                           average_score=average_score)





@app.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    form = SignupForm()
    if form.validate_on_submit():
        name=request.form.get("name")
        email= request.form.get("email")
        password = request.form.get("password")
        user=User(name=name,email=email,password=generate_password_hash(password))
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
    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user_information=db_session.execute(f"SELECT * FROM book_user WHERE email ='{email}'").fetchall()
            if check_password_hash(user_information[0][3],password):
               session["id"]=user_information[0][0]
               session["name"] = user_information[0][1]
               session["email"] = user_information[0][2]
               session.modified=True
               form_search = SearchForm()
               return redirect(url_for('welcome'))
    else:
        form = LoginForm()
        return render_template('login_form.html', form=form)


#manager

@app.route('/api/<isbn>')
def api(isbn):
    book_search=db_session.execute(f"SELECT * FROM books WHERE isbn ='{isbn}'").fetchone()
    review_count=db.session.execute(f"SELECT review_text FROM reviews_table WHERE id_review ='{book_search.isbn}'").rowcount
    average_score=db.session.execute(f"SELECT review_score FROM reviews_table WHERE id_review ='{book_search.isbn}'").fetchone()

    return jsonify(
        {
            "title": book_search.title,
            "author": book_search.author,
            "year":book_search.year,
            "isbn": book_search.isbn,
            "review_count": review_count,
            "average_score": average_score
        }
    )




if __name__== "__main__":
    with app.app_context():
        #main()
        app.run("127.0.0.1",port=5000,debug=True)






#api key 8fuK25fWwRuPi04o6cD1pA