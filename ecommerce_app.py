from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# ----------------------
# Database Models
# ----------------------
# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/elynfoo/ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

# add to cart
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)
    product = db.relationship("Product")

# add customer detail
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)

#add an order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"))
    customer = db.relationship("Customer", backref="orders")
    total = db.Column(db.Float, nullable=False)

#track product in each order
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, nullable=False)

    order = db.relationship("Order", backref="items")
    product = db.relationship("Product")

# ----------------------
# Routes
# ----------------------
# Homepage route
@app.route("/")
def home():
    products = Product.query.all()
    return render_template("ecommerce/home.html", products=products)

# Add product to cart
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):
    item = CartItem(product_id=product_id, quantity=1)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for("cart"))

# View cart
@app.route("/cart")
def cart():
    items = CartItem.query.all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template("ecommerce/cart.html", items=items, total=total)


@app.route('/clear_cart', methods=['GET'])
def clear_cart():
    # Delete all cart items (global cart)
    CartItem.query.delete()
    db.session.commit()
    return redirect(url_for('cart'))



@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")

        # Calculate total before clearing cart
        items = CartItem.query.all()
        total = sum(item.product.price * item.quantity for item in items)

        # Save customer
        customer = Customer(name=name, email=email, address=address)
        db.session.add(customer)
        db.session.commit() # commit so order.id is available
        # ✅ Create and commit order first
        order = Order(customer_id=customer.id, total=total)
        db.session.add(order)
        db.session.commit()   # ensures order.id exists

        # ✅ Now add order items linked to this order
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.session.add(order_item)

        # Clear cart
        CartItem.query.delete()
        db.session.commit()
        return redirect(url_for("confirmation", customer_id=customer.id))
    return render_template("ecommerce/checkout.html")


@app.route("/confirmation")
def confirmation():
    customer_id = request.args.get("customer_id")
    customer = Customer.query.get(customer_id)
    if customer is None:
        return "Customer not found", 404

    order = Order.query.filter_by(customer_id=customer.id).order_by(Order.id.desc()).first()
    return render_template("ecommerce/confirmation.html", customer=customer, order=order)


# ----------------------
# Initialize Database
# ----------------------
with app.app_context():
        db.create_all()
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Add sample products if none exist
        if Product.query.count() == 0:
            sample_products = [
                Product(name="Laptop", price=9.99),
                Product(name="Headphones", price=19.99),
                Product(name="Smartphone", price=99.99),
            ]
            db.session.add_all(sample_products)
            db.session.commit()
    app.run(debug=True)
