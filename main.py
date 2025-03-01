#contains main endpoints CREATE READ UPDATE DELETE
# main.py: Updated with new models and config
from flask import request, jsonify
from config import app, db
from models import User, Ingredient, PantryIngredient, Recipe, RecipeIngredient, Review, UserFavoriteRecipe
from flask_migrate import Migrate

migrate = Migrate(app, db)

##### Pantry Page Endpoints #####
@app.route("/get_pantry/<int:user_id>", methods=["GET"])
def get_pantry(uid):
    pantry_ingredients = PantryIngredient.query.filter_by(user_id=uid).all()
    if not pantry_ingredients:
        return jsonify({"message": "No pantry items found for this user."}), 404
    
    ingredients = [item.to_json() for item in pantry_ingredients]
    return jsonify({"pantry": ingredients})

@app.route("/update_pantry/<int:user_id>", methods=["PATCH"])
def update_pantry(uid):
    data = request.json
    added_ingredients = data.get("addedIngredients")
    updated_ingredients = data.get("updatedIngredients")
    deleted_ingredients = data.get("deletedIngredients")

    for ingredient in added_ingredients:
        if not add_pantry_ingredient(uid, ingredient_id=ingredient[0], quantity=ingredient[1], unit=ingredient[2]):
            return jsonify({"message": "Failed to add ingredient with id=" + str(ingredient[0])})
        
    for ingredient in updated_ingredients:
        if not update_pantry_ingredient(uid, ingredient_id=ingredient[0], quantity=ingredient[1], unit=ingredient[2]):
            return jsonify({"message": "Failed to update ingredient with id=" + str(ingredient[0])})
        
    for ingredient in deleted_ingredients:
        remove_pantry_ingredient(uid, ingredient_id=ingredient)

    return jsonify({"message": "Successfully updated pantry."})

##### Recipe Search Page Endpoints #####
@app.route("/generate_recipes/<int:user_id>", methods=["POST"])
def generate_recipes(uid):
    return jsonify({"message": "Method not yet implemented."})

@app.route("/save_recipe/<int:user_id>", methods=["POST"])
def save_recipe(uid):
    # get recipe information

    # create recipe

    # create ingredients (if not already created in db)

    # create recipe ingredients
    return jsonify({"message": "Method not yet implemented."})

##### Account Page Endpoints #####
@app.route("/update_preferences/<int:user_id>", methods=["PATCH"])
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

##### Signup/Login Page #####
@app.route("/create_account", methods=["POST"])
def create_account():
    data = request.json
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
#    password = data.get("hashedPassword")
    
    if not first_name or not last_name or not email:
        return jsonify({"message": "Please fill out all required fields (firstName, lastName, email)."}), 400
    
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
#        password = password,
        is_vegetarian=data.get("isVegetarian", False),
        is_nut_free=data.get("isNutFree", False),
        is_gluten_free=data.get("isGlutenFree", False)
    )
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User created successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    password = data.get("hashedPassword")
    email = data.get("email")

    # check valid values were passed
    if not password or not email:
        return jsonify({"message": "Please fill all fields (email, hashedPassword)"})

    # find user profile record in database
    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify({"message": "User email could not be found."})

    # check if password is correct
    if user.password == password:
        return jsonify({"message": "User successfully authenticated.",
                        "user_id": user.user_id})
    else:
        return jsonify({"message": "Password was incorrect."})



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

# def get_users():
#     users = User.query.all()
#     json_users = [user.to_json() for user in users]
#     return jsonify({"users": json_users})
#
# def delete_user(user_id):
#     user = User.query.get(user_id)
#     if not user:
#         return jsonify({"message": "User not found."}), 404
#
#     db.session.delete(user)
#     db.session.commit()
#     return jsonify({"message": "User deleted successfully."})
#
# def get_recipes():
#     recipes = Recipe.query.all()
#     return jsonify([recipe.to_json() for recipe in recipes])





if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()
    app.run(debug=True)