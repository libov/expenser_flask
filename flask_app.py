from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from wtforms import StringField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from datetime import *
import numpy as np

from datamodel import *
 
app = Flask(__name__)
app.app_context().push() # this is to prevent context errors

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:testpassword@localhost/expenses'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db.init_app(app)

app.config['SECRET_KEY'] = 'hard to guess string'

@app.route('/test')
def test():
    return render_template('test.html')

class NameForm(FlaskForm):
    description = StringField('Description', validators=[Required()])
    date = DateField('Date', format='%Y-%m-%d', default = date.today(), validators=[Required()])
    category = SelectField('Category', choices=[[1, "Food"], [2, "Restaurants"]])
    submit = SubmitField('Submit')

@app.route('/expenser', methods=['GET', 'POST'])
def expenser():
    descr = None
    form = NameForm()
    if form.is_submitted():
        descr = form.description.data
        form.description.data = ''

    table = []
    cashflows = Cashflow.query.order_by(desc(Cashflow.date)).all()
    for cf in cashflows:
        row = [cf.amount, cf.date, cf.description, cf.category.name]
        table.append(row)
    print(type(table), len(table))
    return render_template('expenser.html', table=table, form=form, descr=descr)

if __name__ == '__main__':
    app.run(debug=True)
