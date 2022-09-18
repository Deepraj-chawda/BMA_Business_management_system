import json

from BMA import app, db, bcrypt
from BMA.forms import RegistrationForm, LoginForm
from BMA.models import User, Product
from flask import render_template, redirect, url_for, request, flash, request, Response
from flask_login import login_user, current_user, logout_user, login_required
import os
import plotly.express as px
import pandas as pd
import plotly
# <-- Application Routes -->

total = 0

# <-- BMA-HOME Page route -->
@app.route('/BMA-HOME')
@login_required
def home():
    return render_template('index.html')

# <-- Embeded Home Page -->
@app.route('/pages/home')
@login_required
def _home():
    return render_template("pages/home.html")

# <-- Embeded About Page -->
@app.route('/pages/about')
@login_required
def _about():
    return render_template("pages/about.html")

# <-- Embeded Contact Page -->
@app.route('/pages/contact')
@login_required
def _contact():
    return render_template("pages/contact.html")

# <-- Embeded Help Page -->
@app.route('/pages/help')
@login_required
def _help():
    return render_template("pages/help.html")

# <-- Embeded Term&Conditions Page -->
@app.route('/pages/termsAndConditions')
@login_required
def _termsAndConditions():
    return render_template("pages/termsAndConditions.html")

# <-- Embeded Add Products Page -->
@app.route('/pages/addProducts', methods=["GET", "POST"])
@login_required
def _addProducts():
    if request.method == "POST":
        data = request.form
        title = data.get('title').lower()
        if Product.query.filter_by(title=title).first():
            return Response("Already Exists", status=402)
        file = request.files.get("image")
        filename = current_user.username + "_" + data.get("title") + "." + file.filename.split(".")[-1]
        path = os.path.join(app.root_path, "static", "productImages", filename)
        file.save(path)
        stock = data.get("stockAvailable")
        product = Product(title=title, mrp=data.get("mrp"), sp=data.get("sp"), stockAvialable=stock, imageName=filename, author=current_user)
        current_user.totalNumberOfProducts += 1
        db.session.add(product)
        db.session.commit()
        return render_template("pages/addedProduct.html", data=data)
    return render_template("pages/addProducts.html")

# <-- Embeded Analysis Page -->
@app.route('/pages/analysis')
@login_required
def _analysis():
    products = current_user.products
    product_data = pd.DataFrame({
        'Title': [product.title for product in products ],
        'Stock Available': [product.stockAvialable for product in products]
    })
    px.defaults.width = 900
    px.defaults.height = 450
    fig_stock = px.bar(
        product_data,
        x="Title",
        y="Stock Available",
        color="Title",

        range_y=[0, max(product_data['Stock Available'])+5]
    )

    graph_stock = json.dumps(fig_stock, cls=plotly.utils.PlotlyJSONEncoder)
    product_sold = pd.DataFrame({
        'Title': [product.title for product in products],
        'Total Sold': [product.totalSold for product in products]
    })

    product_sold = product_sold.sort_values(by=['Total Sold'],ascending=False)[:10]

    fig_sold = px.bar(
        product_sold,
        x="Title",
        y="Total Sold",
        color="Title",

        range_y=[0, max(product_sold['Total Sold']) + 5]
    )

    graph_sold = json.dumps(fig_sold, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template("pages/analysis.html", graph_stock=graph_stock, graph_sold=graph_sold)


# <-- Embeded Billing System Page -->
@app.route('/pages/billingSystem')
@login_required
def _billingSystem():
    global total
    total = 0
    return render_template("pages/billingSystem.html")

# <-- Embeded Know Your Customer Page -->
@app.route('/pages/knowYourCustomer')
@login_required
def _knowYourCustomer():
    return render_template("pages/knowYourCustomer.html")

# <-- Embeded Know Other Seller Page -->
@app.route('/pages/knowOtherSeller')
@login_required
def _knowOtherSeller():
    return render_template("pages/knowOtherSeller.html")

# <-- Embeded Your Profit Page -->
@app.route('/pages/yourProfit')
@login_required
def _yourProfit():
    return render_template("pages/yourProfit.html")

# <-- Embeded Product Analysis Page -->
@app.route('/pages/productAnalysis')
@login_required
def _productAnalysis():
    products = current_user.products
    return render_template("pages/productAnalysis.html", products=products)

# <-- Embeded Your Profile Page -->
@app.route('/pages/yourProfile')
@login_required
def _yourProfile():
    return render_template("pages/yourProfile.html", user=current_user)

# <-- Embeded Know Your Stock Page -->
@app.route('/pages/knowYourStock')
@login_required
def _knowYourStock():
    return render_template("pages/knowYourStock.html")

# <-- Embeded Update Product Details Page -->
@app.route('/pages/updateProductDetails')
@login_required
def _updateProductDetails():
    return render_template("pages/updateProductDetails.html")

# <-- Login Page -->
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful', 'danger')
    return render_template('login.html', title='Login', form=form)


# <-- SignUp Page -->
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, companyName=form.companyName.data, address=form.address.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created', 'success')
        return redirect('login')
    return render_template('register.html', title='Register', form=form)

# <-- Logout Url -->
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# <-- Search Products -->
@app.route('/search/<string:itemName>', methods=["GET"])
@login_required
def _searchProducts(itemName):
    products = Product.query.filter_by(author=current_user)
    products = products.filter(Product.title.like(f"%{itemName.lower()}%")).order_by(Product.title).all()
    return render_template("pages/search.html", products=products)

# <-- Sold Items -->
@app.route("/sold/<string:itemName>/<int:stock>", methods=["GET"])
@login_required
def sold(itemName, stock):
    products = Product.query.filter_by(author=current_user)
    product  = products.filter_by(title=itemName).first()
    if (product.stockAvialable < stock):
        return Response("Error", status=404)
    product.totalSold += stock
    product.stockAvialable = product.stockAvialable - stock
    db.session.add(product)
    db.session.commit()
    global total
    total += product.sp * stock
    return render_template("pages/sold.html", product=product, stock=stock, total=total)