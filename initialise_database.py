from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://testuser:testpassword@localhost/expenses'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)

app.config['SECRET_KEY'] = 'hard to guess string'

class Balance(db.Model):
    __tablename__ = 'BALANCE'
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date = db.Column(db.Date, nullable=False, unique=True)

class Category(db.Model):
    __tablename__ = 'CATEGORY'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True, nullable=False)
    expenses = db.relationship("Cashflow", backref='category')
    
    def __repr__(self):
        return '<Category %r>' % self.name

class Cashflow(db.Model):
    __tablename__ = 'CASHFLOW'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), nullable=False)
    amount = db.Column(db.Float(precision=2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    booked = db.Column(db.Boolean, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('CATEGORY.id'), nullable=False)

    def __repr__(self):
        return '<Cashflow id %r>' % self.id
    
if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    #admin_role=Role(name='Admin')
    #mod_role=Role(name='Moderator')
    #user_john=User(username='john', rolee=mod_role)
    #user_susan=User(username='susan', rolee=mod_role)
    #user_susan2=User(username='susan2', rolee=admin_role)
    #db.session.add(admin_role)
    #db.session.add(mod_role)
    #db.session.add(user_john)
    #db.session.add(user_susan)
    #db.session.add(user_susan2)
    #db.session.delete(admin_role)
    db.session.commit()
    
    #print(Role.query.all())
    #print(User.query.all())
    #print("Admins:", User.query.filter_by(rolee=admin_role).all())
   # print("Moderators:", User.query.filter_by(rolee=mod_role).all())
    