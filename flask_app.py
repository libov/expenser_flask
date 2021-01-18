from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func, and_
from wtforms import StringField, SelectField, SubmitField, DecimalField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Required, DataRequired, InputRequired
from flask_wtf import FlaskForm
from datetime import *
from decimal import *
import numpy as np
from flask_bootstrap import Bootstrap

from datamodel import *
 
app = Flask(__name__)
app.app_context().push() # this is to prevent context errors

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:testpassword@localhost/expenses'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)

per_page_options=[5,10,15,20,25,30,50,100]

def getCategories():
    category_map={}
    categories = Category.query.all()
    for ctg in categories:
        # here we simply use the Category ID Attribute to count the choices for the form below
        category_map[ctg.id]=ctg.name
    return category_map

class NewExpenseForm(FlaskForm):
    amount = DecimalField('Amount', places=2, validators=[InputRequired()]) # not sure what places=2 is doing.....
    description = StringField('Description', validators=[Required()])
    date = DateField('Date', format='%Y-%m-%d', default = date.today(), validators=[Required()])
    choices=[]
    for id, name in getCategories().items():
        choices.append([id, name])
    category = SelectField('Category', choices=choices)
    booked = BooleanField('Booked', default=False )
    submit = SubmitField('Submit')

class FilterForm(FlaskForm):
    descriptionContains = StringField('Description contains')
    dateFrom = DateField('Date From', format='%Y-%m-%d')
    dateTo = DateField('Date From', format='%Y-%m-%d')
    choices=[]
    for id, name in getCategories().items():
        choices.append([id, name])
    choices.append([999, "Any"])
    category = SelectField('Category', choices=choices)
    booked = SelectField('Booked', choices=[[1, "Yes"], [2, "No"], [3, "Any"]])
    filter = SubmitField('Filter')

def toDate(dateString):
    return datetime.strptime(dateString, "%Y-%m-%d").date()

@app.route('/expenser', methods=['GET', 'POST'])
def expenser():
    per_page = request.args.get('per_page', 10, type=int)

    form = NewExpenseForm()
    if request.method == "POST" and form.submit.data:
        if form.validate():
            amt = form.amount.data
            places = -amt.as_tuple().exponent
            if places != 2:
                TWOPLACES=Decimal('0.01')
                amt = amt.quantize(TWOPLACES)
                if places>2:
                    flash("Warning: More than two decimals given for Cashflow amount. Truncating to {0}".format(amt))
            descr = form.description.data
            dt = form.date.data
            categories = getCategories()
            category =  categories[int(form.category.data)]
            ctg = Category.query.filter_by(name=category).first()
            bkd = form.booked.data
            cf = Cashflow(amount=amt, description=descr, date=dt, category=ctg, booked=bkd)
            db.session.add(cf)
            db.session.commit()
            flash("Successfully submitted: {0} eur for {1} ({2}) on {3}".format(amt, descr, category, form.date.data))
            return redirect(url_for('expenser')+'?per_page='+str(per_page))
        else:
            for error in form.errors:
                print(error, form.errors[error])
                flash("Error(s) for field {0}: {1} ".format(error, str(form.errors[error])))

    descriptionContains = request.args.get('descriptionContains', None, type=str)
    category = request.args.get('category', None, type=int)
    dateFrom = request.args.get('dateFrom', None, type = toDate)
    dateTo = request.args.get('dateTo', None, type = toDate)
    booked = request.args.get('booked', None, type = int)

    cfq = Cashflow.query

    if dateTo:
        cfq = cfq.filter(Cashflow.date <= dateTo)
    if dateFrom:
        cfq = cfq.filter(Cashflow.date >= dateFrom)
    if booked:
        if booked != 3:
            if booked == 1:
                booked=True
            elif booked == 2:
                booked=False
            cfq =  cfq.filter(Cashflow.booked == booked)
    if descriptionContains:
        cfq = cfq.filter(Cashflow.description.contains(descriptionContains))
    if category:
        if (category != 999):
            ctg = Category.query.filter_by(id=category).first()
            cfq = cfq.filter(Cashflow.category == ctg)

    page = request.args.get('page', 1, type=int)
    pagination = cfq.order_by(desc(Cashflow.date)).paginate(page, per_page=per_page, error_out=False)
    cashflows = pagination.items
    if not category:
        category = 999
    if not booked:
        booked = 3
    filterForm = FilterForm(descriptionContains=descriptionContains, category=category, dateFrom=dateFrom, dateTo=dateTo, booked=booked)
    return render_template('expenser-boostrap.html', form=form, FilterForm=filterForm, pagination=pagination, cashflows=cashflows, balance=calculateBalance(), per_page=per_page, per_page_options=per_page_options,
                           descriptionContains=descriptionContains, category=category, dateFrom=dateFrom, dateTo=dateTo, booked=booked)

@app.route('/flipBookedFlag/<id>', methods = ['POST'])
def flipBookedFlag(id):
    cf = Cashflow.query.filter_by(id=id).first()
    cf.booked = not cf.booked
    db.session.add(cf)
    db.session.commit()
    print("INFO: changed booking status of Cashflow with id={0}".format(cf.id))
    return ''

def calculateBalance():
    result=Cashflow.query.with_entities(Cashflow.booked, func.sum(Cashflow.amount)).group_by(Cashflow.booked).all()
    for res in result:
        bkd = res[0]
        amt = res[1]
        if bkd == True:
            return str(Decimal(str(287.27))+amt) # TODO: starting balance shouldn't be hard-coded
    return 0

if __name__ == '__main__':
    app.run(debug=True)
