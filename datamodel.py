from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Balance(db.Model):
    __tablename__ = 'BALANCE'
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Numeric(10,2), nullable=False)
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
    amount = db.Column(db.Numeric(10,2), nullable=False)
    date = db.Column(db.Date, nullable=False)
    booked = db.Column(db.Boolean, nullable=False, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('CATEGORY.id'), nullable=False)

    def __repr__(self):
        return '<Cashflow id %r>' % self.id