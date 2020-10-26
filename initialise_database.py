from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as ET
import datetime
from datamodel import *
import sys
from decimal import Decimal

app = Flask(__name__)
app.app_context().push() # this is to prevent context errors

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:testpassword@localhost/expenses'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db.init_app(app)

app.config['SECRET_KEY'] = 'hard to guess string'

def initialise_database():
    db.drop_all()
    db.create_all()

def migrate_database():
    
    # read the source XML-database
    tree = ET.parse('expenses.xml')
    root = tree.getroot()
    i=0

    # as the first step we need to write the categories, because it is used
    # as a foreign key

    # first, determine the categories
    categories = []
    for expense in root:
        if expense.tag != "expense": continue
        category =  expense.find("category").text
        if category not in categories:
            categories.append(category)
    categories.sort()

    # write to the database
    for category in categories:
        cat = Category(name=category)
        db.session.add(cat)

    # now write the expenses
    for expense in root:
        if expense.tag != "expense": continue
        amount = expense.find("amount").text
        day = int(expense.find("date/day").text)
        month = int(expense.find("date/month").text)
        year = int(expense.find("date/year").text)
        withdrawn = expense.find("withdrawn").text
        category =  expense.find("category").text
        description =  expense.find("description").text

        # to avoid errors when there is no description
        if description == None:
            description=""

        # convert Yes/No to Bool
        booked=False
        if withdrawn == "Yes":
            booked = True

        # sanity check - should be exactly two digits
        dec = amount[amount.find('.')+1:]
        if len(dec)!=2:
            print("ERROR: the cashflows must have exactly two digits. Cashflow amount {0} with {1} decimals (id={3})".format(amount, len(dec), expense.find("id").text))
            sys.exit()

        cat = Category.query.filter_by(name=category).first()

        cf = Cashflow(amount=Decimal(amount), description=description, booked=booked, date=datetime.date(year, month, day), category=cat)

        db.session.add(cf)

if __name__ == '__main__':

    initialise_database()
    migrate_database()
    db.session.commit()
