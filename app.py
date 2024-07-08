from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
import RPi.GPIO as GPIO
import atexit
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    image = db.Column(db.String(100))
    gpio_pin = db.Column(db.Integer)  # New attribute for GPIO pin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    items = Item.query.all()
    return render_template('admin.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        gpio_pin = request.form['gpio_pin']
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_item = Item(name=name, price=price, description=description, image=filename, gpio_pin=gpio_pin)
            db.session.add(new_item)
            db.session.commit()
            return redirect(url_for('admin'))
    return render_template('add_item.html')

@app.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/modify_item/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_item(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    item = Item.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        item.gpio_pin = request.form['gpio_pin']
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            item.image = filename
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('modify_item.html', item=item)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        address = request.form['address']
        payment = request.form['payment']
        items_checked_out = session.get('cart', [])  # Example list of item IDs being checked out

        for item_id in items_checked_out:
            item = Item.query.get(item_id)
            if item and item.gpio_pin:
                GPIO.output(item.gpio_pin, GPIO.HIGH)
        
        flash('Checkout successful. GPIO pins triggered.', 'success')
        session.pop('cart', None)  # Clear the cart after checkout
        return redirect(url_for('index'))

    return render_template('checkout.html')

@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    cart = session.get('cart', [])
    cart.append(item_id)
    session['cart'] = cart
    flash('Item added to cart', 'success')
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def cleanup_gpio():
    GPIO.cleanup()

atexit.register(cleanup_gpio)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
