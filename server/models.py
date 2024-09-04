from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Update `server/models.py` to establish the model relationships. Since a
# `RestaurantPizza` belongs to a `Restaurant` and a `Pizza`, configure the model 
# to cascade deletes.
#nullbale=false
# cascade = delete
# Database-level cascade deletes are set on ForeignKey:

# project_id = Column(
#     Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False
# )
# This says: ON DELETE of the row I'm referencing CASCADE and delete this row too. Remember passive_deletes=True!

# ORM-level cascade deletes are set on relationship:
# tasks = relationship(
#     "Task", back_populates="project", cascade="all, delete-orphan"
# )
# This says: Cascade the deletion of this object to these related objects.

class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)

    # add relationship
    # A Restaurant has many Pizzas through RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='restaurant', cascade='all, delete-orphan')
    pizzas = association_proxy('restaurant_pizzas', 'pizza')

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.restaurant', '-restaurant_pizzas.pizza')

    def __repr__(self):
        return f"<Restaurant {self.name}>"


class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String)

    # add relationship
    # A Pizza has many Restaurants through RestaurantPizza
    restaurant_pizzas = db.relationship('RestaurantPizza', back_populates='pizza', cascade='all, delete-orphan')
    restaurants = association_proxy('restaurant_pizzas', 'restaurant')

    # add serialization rules
    serialize_rules = ('-restaurant_pizzas.pizza', '-restaurant_pizzas.restaurant')

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # foreign keys
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # add relationships
    # A RestaurantPizza belongs to a Restaurant and belongs to a Pizza
    restaurant = db.relationship('Restaurant', back_populates='restaurant_pizzas')
    pizza = db.relationship('Pizza', back_populates='restaurant_pizzas')

    # add serialization rules
    serialize_rules = ('-restaurant.restaurant_pizzas', '-pizza.restaurant_pizzas')

    # add validation
    # Add validations to the RestaurantPizza model: must have a price between 1 and 30
    @validates('price')
    def validate_price(self, key, user_price):
        if not (1 <= user_price <= 30):
            raise ValueError('Price must be between 1 and 30')
        return user_price


