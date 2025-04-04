#contains main endpoints CREATE READ UPDATE DELETE
# main.py: Updated with new models and config
from flask import request, jsonify
from config import app, db
from models import User, Ingredient, PantryIngredient, Recipe, RecipeIngredient, Review, UserFavoriteRecipe
from flask_migrate import Migrate
import os
from flask_bcrypt import Bcrypt
import mysql.connector
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import unset_jwt_cookies
from recipe import generate_recipes_from_ingredients
from recipe import getListOfIngredients


db = mysql.connector.connect(
    host= os.environ.get("DB_HOST"),
    user= os.environ.get("DB_USER"),
    password= os.environ.get("DB_PASS"),
    database= os.environ.get("DB_NAME")
) 
cursor = db.cursor()

migrate = Migrate(app, db)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_Secret")
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    fName = data.get("first_name")
    lName = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        return jsonify({"message": "User already exists"}), 400

    cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)", (fName, lName, email, hashed_password))
    db.commit()

    return jsonify({"message": "User registered successfully"}), 201


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT email, password, user_id FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    
    if not user or not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=user["email"])
    return jsonify({"access_token": access_token})

@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)  # Clears the JWT from cookies
    return response, 200


##### Pantry Page Endpoints #####
@app.route("/get_pantry/<int:uid>", methods=["GET"])
@jwt_required()
def get_pantry(uid):
    pantry_ingredients = PantryIngredient.query.filter_by(user_id=uid).all()
    if not pantry_ingredients:
        return jsonify({"message": "No pantry items found for this user."}), 404
    
    ingredients = [item.to_json() for item in pantry_ingredients]
    return jsonify({"pantry": ingredients})

@app.route("/update_pantry/<int:uid>", methods=["PATCH"])
@jwt_required()
def update_pantry(uid):
    data = request.json
    added_ingredients = data.get("addedIngredients")
    updated_ingredients = data.get("updatedIngredients")
    deleted_ingredients = data.get("deletedIngredients")

    for ingredient in added_ingredients:
        if not add_pantry_ingredient(uid, ingredient_name=ingredient[0], quantity=ingredient[1], unit=ingredient[2]):
            return jsonify({"message": "Failed to add ingredient with name=" + str(ingredient[0])})
        
    for ingredient in updated_ingredients:
        if not update_pantry_ingredient(uid, ingredient_name=ingredient[0], quantity=ingredient[1], unit=ingredient[2]):
            return jsonify({"message": "Failed to update ingredient with name=" + str(ingredient[0])})
        
    for ingredient in deleted_ingredients:
        remove_pantry_ingredient(uid, ingredient_name=ingredient)

    return jsonify({"message": "Successfully updated pantry."})


@app.route("/save_recipe/<int:uid>", methods=["POST"])
@jwt_required()
def save_recipe(uid):
    # get recipe information

    # create recipe

    # create ingredients (if not already created in db)

    # create recipe ingredients
    return jsonify({"message": "Method not yet implemented."})

##### Account Page Endpoints #####
@app.route("/update_preferences/<int:uid>", methods=["PATCH"])
@jwt_required()
def update_preferences(uid):
    user = User.query.get(uid)
    if not user:
        return jsonify({"message": "User not found."}), 404
    
    data = request.json
    user.is_vegetarian = data.get("isVegetarian", user.is_vegetarian)
    user.is_nut_free = data.get("isNutFree", user.is_nut_free)
    user.is_gluten_free = data.get("isGlutenFree", user.is_gluten_free)

    db.session.commit()
    return jsonify({"message": "User updated successfully."})

@app.route("/delete_user/<int:uid>", methods=["POST"])
@jwt_required()
def delete_user(uid):
    user = User.query.get(uid)

    if user is None:
        return jsonify({"message": "A user could not be found with the given user_id"})
    
    # delete the user's pantry ingredients
    ingredients = PantryIngredient.query.filter_by(user_id=uid)
    for item in ingredients:
        db.session.delete(item)

    # delete the recipes saved by the user (?)
    # recipes = Recipe.query.filter_by(user_id=uid)
    # for item in recipes:
    #    db.session.delete(item)

    # delete the user
    db.session.delete(user)

    db.session.commit()

    return jsonify({"message": "User successfully deleted."})

@app.route("/recipe/generate", methods=["POST"])
@jwt_required()
def generate():
    data = request.json
    user_query = data.get("user_query")
    current_user_email = get_jwt_identity()
    current_user = User.query.filter_by(email = current_user_email).first()
    # get the list of ingreidents
    # ingredients = getListOfIngredients(current_user_email)
    pantry_ingredients = PantryIngredient.query.filter_by(user_id=current_user.user_id).all()
    if not pantry_ingredients:
        ingredients = ""
    else:
        ingredients = ",".join([item.name for item in pantry_ingredients])
    print(ingredients)
    # generate 3 recipes using the ingredients and user query
    result = generate_recipes_from_ingredients(user_query,ingredients)
    return result


##### Additional Helper Functions #####

def add_pantry_ingredient(uid, ingredient_id, quantity, unit):
    if not ingredient_id or quantity is None or not unit:
        return False

    new_item = PantryIngredient(user_id=uid, ingredient_id=ingredient_id, quantity=quantity, unit=unit)
    try:
        db.session.add(new_item)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False

def update_pantry_ingredient(uid, ingredient_id, quantity, unit):
    if not ingredient_id or quantity is None or not unit:
        return False

    pantry_item = PantryIngredient.query.filter_by(user_id=uid, ingredient_id=ingredient_id).first()
    if not pantry_item:
        return False

    pantry_item.quantity = quantity
    pantry_item.unit = unit
    db.session.commit()
    return True

def remove_pantry_ingredient(uid, ingredient_id):
    if not ingredient_id:
        return True # ingredient is not in db, so return true

    pantry_item = PantryIngredient.query.filter_by(user_id=uid, ingredient_id=ingredient_id).first()
    if not pantry_item:
        return True # again, ingredient is not in db, so return true

    db.session.delete(pantry_item)
    db.session.commit()
    return True


if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()
    app.run(debug=True)