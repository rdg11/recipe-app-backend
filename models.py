#contains database models and interaction
from config import db

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(80), unique = False, nullable = False)
    last_name = db.Column(db.String(80), unique = False, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    
    def to_json(self):
        return {
            "id": self.id,
            "firstname": self.first_name,
            "lastname": self.last_name,
            "email": self.email
        }

class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True, nullable = False)
    contains_nuts = db.Column(db.Integer, unique = False, nullable = False)
    contains_gluten = db.Column(db.Integer, unique = False, nullable = False)
    contains_meat = db.Column(db.Integer, unique = False, nullable = False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "contains_nuts": self.contains_nuts,
            "contains_gluten": self.contains_gluten,
            "contains_meat": self.contains_meat
        }

class PantryIngredient(db.Model):
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key = True, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), primary_key = True, nullable = False)
    quantity = db.Column(db.Float, nullable = False)
    unit = db.Column(db.String, nullable = False)

    def to_json(self):
        return {
            "ingredient_id": self.ingredient_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "unit": self.unit
        }