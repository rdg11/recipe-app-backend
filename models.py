#contains database models and interaction
from config import db
import datetime

class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
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
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(64), unique = True, nullable = False)
    contains_nuts = db.Column(db.Integer, unique = False, nullable = False, default = 0)
    contains_gluten = db.Column(db.Integer, unique = False, nullable = False, default = 0)
    contains_meat = db.Column(db.Integer, unique = False, nullable = False, default = 0)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key = True, nullable = False)
    quantity = db.Column(db.Float, nullable = False, default = 0.0)
    unit = db.Column(db.String(50), nullable = False)

    def to_json(self):
        return {
            "ingredient_id": self.ingredient_id,
            "user_id": self.user_id,
            "quantity": self.quantity,
            "unit": self.unit
        }
    
class RecipeIngredient(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key = True, nullable = False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key = True, nullable = False)
    quantity = db.Column(db.Float, nullable = True, default = None)
    unit = db.Column(db.String(50), nullable = True, default = None)
    
    def to_json(self):
        return {
            "recipe_id": self.recipe_id,
            "ingredient_id": self.ingredient_id,
            "quantity": self.quantity,
            "unit": self.unit
        }

class Recipe(db.Model):
    recipe_id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String(255))   
    steps = db.Column(db.String(2047))
    is_vegan = db.Column(db.Integer, default = 0)
    is_gluten_free = db.Column(db.Integer, default = 0)
    is_nut_free = db.Column(db.Integer, default = 0) 

    def to_json(self):
        return {
            "recipe_id": self.recipe_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "is_vegan": self.is_vegan,
            "is_gluten_free": self.is_gluten_free,
            "is_nut_free": self.is_nut_free
        }

class Review(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key = True, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key = True, nullable = False)
    rating = db.Column(db.Integer, nullable = True, default=None)
    review_text = db.Column(db.String(511), nullable = True)
    created_at = db.Column(db.DateTime, default = datetime.datetime.now())

    def to_json(self):
        return {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at
        }

class UserFavoriteRecipe(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key = True, nullable = False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key = True, nullable = False)

    def to_json(self):
        return {
            "user_id": self.user_id,
            "recipe_id": self.recipe_id
        }

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True, nullable = False)
    first_name = db.Column(db.String(255), nullable = False)
    last_name = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), unique = True, nullable = False)
    isVegetarian = db.Column(db.Integer, nullable = False, default = 0)
    isNutFree = db.Column(db.Integer, nullable = False, default = 0)
    isGlutenFree = db.Column(db.Integer, nullable = False, default = 0)

    def to_json(self):
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "isVegetarian": self.isVegetarian,
            "isNutFree": self.isNutFree,
            "isGlutenFree": self.isGlutenFree
        }