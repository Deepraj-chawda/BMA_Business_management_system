from BMA import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))

class User(db.Model, UserMixin):
  id          = db.Column(db.Integer, primary_key=True)
  username    = db.Column(db.String(20), unique=True, nullable=False)
  email       = db.Column(db.String(120), unique=True, nullable=False)
  password    = db.Column(db.String(60), nullable=False)
  address     = db.Column(db.String(60), nullable=False)
  companyName = db.Column(db.String(60), nullable=False)
  likes       = db.Column(db.Integer, nullable=False, default=0)
  totalNumberOfProducts = db.Column(db.Integer, nullable=False, default=0)
  customersVisited = db.Column(db.Integer, nullable=False, default=0)
  products    = db.relationship('Product', backref='author', lazy=True)
  customers   = db.relationship('Customer', backref='author', lazy=True)

  def __repr__(self):
    return f"User ({self.username}, {self.email})"

class Product(db.Model):
  id             = db.Column(db.Integer, primary_key=True)
  title          = db.Column(db.String(20), unique=True)
  mrp            = db.Column(db.Float, nullable=False)
  sp             = db.Column(db.Float, nullable=False)
  stockAvialable = db.Column(db.Integer, nullable=False)
  imageName      = db.Column(db.String(40), nullable=False)
  totalSold      = db.Column(db.Integer, nullable=False, default=0)
  userId         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Customer(db.Model):
  id                 = db.Column(db.Integer, primary_key=True)
  name               = db.Column(db.String(20))
  email              = db.Column(db.String(20), unique=True, nullable=False, default="None")
  lastShop           = db.Column(db.Integer, nullable=False)
  totalShoppedAmount = db.Column(db.Float, nullable=False)
  totalVisit         = db.Column(db.Integer, nullable=False)
  products           = db.relationship('ProductPurchased', backref='customer', lazy=True)
  userId             = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ProductPurchased(db.Model):
  id               = db.Column(db.Integer, primary_key=True)
  title            = db.Column(db.String(20), nullable=False)
  price            = db.Column(db.Float, nullable=False)
  numberOfProducts = db.Column(db.Integer, nullable=False)
  customerId       = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)