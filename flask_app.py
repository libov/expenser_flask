from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from wtforms import StringField, SelectField, SubmitField, DecimalField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import Required
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

def getCategories():
    category_map={}
    categories = Category.query.all()
    for ctg in categories:
        # here we simply use the Category ID Attribute to count the choices for the form below
        category_map[ctg.id]=ctg.name
    return category_map

class NewExpenseForm(FlaskForm):
    amount = DecimalField('Amount', validators=[Required()])
    description = StringField('Description', validators=[Required()])
    date = DateField('Date', format='%Y-%m-%d', default = date.today(), validators=[Required()])
    choices=[]
    for id, name in getCategories().items():
        choices.append([id, name])
    category = SelectField('Category', choices=choices)
    booked = BooleanField('Booked', default=False )
    submit = SubmitField('Submit')

@app.route('/expenser', methods=['GET', 'POST'])
def expenser():
    form = NewExpenseForm()
    if form.is_submitted():
        amt = form.amount.data
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
        return redirect(url_for('expenser'))

    table = []
    cashflows = Cashflow.query.order_by(desc(Cashflow.date)).all()
    #cashflows = Cashflow.query.paginate(1,20,False)
    for cf in cashflows:
        to_YesNo=lambda x: 'Yes' if x else 'No'
        row = [cf.amount, cf.description, cf.category.name, cf.date, to_YesNo(cf.booked)]
        table.append(row)
    return render_template('expenser-boostrap.html', table=table, form=form)

if __name__ == '__main__':
    app.run(debug=True)
