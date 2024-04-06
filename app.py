from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask import request
app = Flask(__name__)
username = 'mysql'
password = 'nqXQ0ur6kodwkHe2ZryxEEHOMYvkY9w0PdJmrXFW1sM='
hostname = 'mysql-gaaq'  # Use the actual hostname from the image you provided
port = '3306'  # Use the actual port if different
database = 'mysql'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}'

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    desired_inventory = db.Column(db.Integer, nullable=False)
    realtime_inventory = db.Column(db.Integer, nullable=False)
    supplier_inventory = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Product %r>' % self.name

class User_products(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User_products.query.get(int(user_id))

@app.route('/', methods=['GET'])
def index():
    search_query = request.args.get('query')
    if search_query:
        # Filter products based on search query
        products = Product.query.filter(Product.name.ilike(f'%{search_query}%')).all()
    else:
        # If no search query, retrieve all products
        products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        desired_inventory = int(request.form['desired_inventory'])
        realtime_inventory = int(request.form['realtime_inventory'])
        supplier_inventory = desired_inventory - realtime_inventory

        new_product = Product(name=name, price=price, desired_inventory=desired_inventory,
                              realtime_inventory=realtime_inventory, supplier_inventory=supplier_inventory)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = float(request.form['price'])
        product.desired_inventory = int(request.form['desired_inventory'])
        product.realtime_inventory = int(request.form['realtime_inventory'])
        product.supplier_inventory = product.desired_inventory - product.realtime_inventory

        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User_products.query.filter_by(username=username).first()

        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Invalid password')
        else:
            flash('User not found')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User_products.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
