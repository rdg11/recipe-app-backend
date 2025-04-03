from config import db
import datetime


# Users Table
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    is_vegetarian = db.Column(db.Boolean)
    is_nut_free = db.Column(db.Boolean)
    is_gluten_free = db.Column(db.Boolean)

    user_favorite_recipes = db.relationship(
        'UserFavoriteRecipe',
        back_populates='user',
        overlaps="favorite_recipes"
    )

    favorite_recipes = db.relationship(
        'Recipe',
        secondary='user_favorite_recipes',
        back_populates='favorited_by',
        overlaps="user,user_favorite_recipes"
    )

    def to_json(self):
        return {
            "id": self.user_id,
            "firstname": self.first_name,
            "lastname": self.last_name,
            "email": self.email,
            "password": self.password,
            "isVegetarian": self.is_vegetarian,
            "isNutFree": self.is_nut_free,
            "isGlutenFree": self.is_gluten_free,
            "favoriteRecipes": [recipe.recipe_id for recipe in self.favorite_recipes]
        }

# Ingredients Table
class Ingredient(db.Model):
    __tablename__ = 'ingredient'

    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    contains_nuts = db.Column(db.Boolean)
    contains_gluten = db.Column(db.Boolean)
    contains_meat = db.Column(db.Boolean)

    def to_json(self):
        return {
            "id": self.ingredient_id,
            "name": self.name,
            "containsNuts": self.contains_nuts,
            "containsGluten": self.contains_gluten,
            "containsMeat": self.contains_meat
        }

# Pantry Ingredients Table (Many-to-Many between Users & Ingredients)
class PantryIngredient(db.Model):
    __tablename__ = 'pantry_ingredient'

    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    quantity = db.Column(db.Numeric(10, 2))
    unit = db.Column(db.String(50))

    user = db.relationship('User', backref=db.backref('pantry_ingredients', lazy=True))
    ingredient = db.relationship('Ingredient', backref=db.backref('pantry_ingredients', lazy=True))

    def to_json(self):
        return {
            "ingredientId": self.ingredient_id,
            "userId": self.user_id,
            "quantity": float(self.quantity),
            "unit": self.unit
        }

# Recipes Table
class Recipe(db.Model):
    __tablename__ = 'recipe'

    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    steps = db.Column(db.Text)
    is_vegetarian = db.Column(db.Boolean)
    is_gluten_free = db.Column(db.Boolean)
    is_nut_free = db.Column(db.Boolean)
    
    user_favorite_recipes = db.relationship(
        'UserFavoriteRecipe',
        back_populates='recipe',
        overlaps="favorite_recipes"
    )

    favorited_by = db.relationship(
        'User',
        secondary='user_favorite_recipes',
        back_populates='favorite_recipes',
        overlaps="user,user_favorite_recipes"
    )

    def to_json(self):
        return {
            "id": self.recipe_id,
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "is_vegetarian": self.is_vegetarian,
            "is_gluten_free": self.is_gluten_free,
            "is_nut_free": self.is_nut_free
        }

# Recipe Ingredients Table (Many-to-Many between Recipes & Ingredients)
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredient'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.ingredient_id'), primary_key=True)
    quantity = db.Column(db.Numeric(10, 2))
    unit = db.Column(db.String(50))

    recipe = db.relationship('Recipe', backref=db.backref('recipe_ingredients', lazy=True))
    ingredient = db.relationship('Ingredient', backref=db.backref('recipe_ingredients', lazy=True))

    def to_json(self):
        return {
            "recipeId": self.recipe_id,
            "ingredientId": self.ingredient_id,
            "quantity": float(self.quantity),
            "unit": self.unit
        }

# Reviews Table (Many-to-Many between Users & Recipes)
class Review(db.Model):
    __tablename__ = 'reviews'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))
    recipe = db.relationship('Recipe', backref=db.backref('reviews', lazy=True))

    def to_json(self):
        return {
            "recipeId": self.recipe_id,
            "userId": self.user_id,
            "rating": self.rating,
            "reviewText": self.review_text,
            "createdAt": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# User Favorite Recipes Table (Many-to-Many between Users & Recipes)
class UserFavoriteRecipe(db.Model):
    __tablename__ = 'user_favorite_recipes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.recipe_id'), primary_key=True)

    user = db.relationship("User", back_populates="user_favorite_recipes", overlaps="favorite_recipes")
    recipe = db.relationship("Recipe", back_populates="user_favorite_recipes", overlaps="favorited_by,favorite_recipes")


    def to_json(self):
        return {
            "userId": self.user_id,
            "recipeId": self.recipe_id
        }
