from flask import Flask, request, render_template
from wtforms import StringField, SelectField, SubmitField
from wtforms.fields.html5 import DateField
from wtforms.validators import Required
from flask_wtf import FlaskForm
from datetime import *
import numpy as np

from flask_sqlalchemy import SQLAlchemy
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:testpassword@localhost/expenses'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

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
    return render_template('expenser.html', table=[[1.1,2.1,3.1], [10,20,30], [100,200,3000]], form=form, descr=descr)

if __name__ == '__main__':
    app.run(debug=True)