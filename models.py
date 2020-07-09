
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db=SQLAlchemy()

class book(db.Model):
    __tablename__="books"
    isbn = db.Column(db.String,primary_key= True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    year = db.Column(db.Integer)

class User(db.Model, UserMixin):
    __tablename__ = 'book_user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_admin(self):
        return self.is_admin
    def __repr__(self):
        return f'<User {self.email}>'
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    @staticmethod
    def get_by_id(id):
        return User.query.get(id)
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

class Review (db.Model):
    __tablename__="reviews_table"
    id=db.Column(db.Integer,primary_key=True)
    id_review = db.Column(db.String(), db.ForeignKey(f'{book.__tablename__}.isbn'))
    review_text=db.Column(db.String())
    review_score = db.Column(db.Integer)
    date=db.Column(db.DateTime,default=datetime.utcnow)
    user= db.Column(db.Integer, db.ForeignKey(f'{User.__tablename__}.id'))
