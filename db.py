import csv
from application import db_session
from models import db


def main():
    db.drop_all()
    db.create_all()
    with open("books.csv") as f:
        next(f)#skip header
        reader=csv.reader(f)
        for isbn,title,author,year in reader:
            db_session.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                       {"isbn": isbn, "title": title, "author": author, "year": int(year)})
            db_session.commit()
if __name__== "__main__":
    main()