#contains main endpoints CREATE READ UPDATE DELETE
# main.py: Updated with new models and config
from flask import request, jsonify
from config import app, db
from models import User, Ingredient, PantryIngredient, Recipe, RecipeIngredient, Review, UserFavoriteRecipe
from flask_migrate import Migrate

migrate = Migrate(app, db)

##### User (Profile) Endpoints #####
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    json_users = [user.to_json() for user in users]
    return jsonify({"users": json_users})

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    email = data.get("email")
    
    if not first_name or not last_name or not email:
        return jsonify({"message": "Please fill out all required fields (firstName, lastName, email)."}), 400
    
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
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

@app.route("/users/<int:user_id>", methods=["PATCH"])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    data = request.json
    user.first_name = data.get("firstName", user.first_name)
    user.last_name = data.get("lastName", user.last_name)
    user.email = data.get("email", user.email)
    user.is_vegetarian = data.get("isVegetarian", user.is_vegetarian)
    user.is_nut_free = data.get("isNutFree", user.is_nut_free)
    user.is_gluten_free = data.get("isGlutenFree", user.is_gluten_free)

    db.session.commit()
    return jsonify({"message": "User updated successfully."})

@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found."}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully."})

##### Pantry Endpoints #####
@app.route('/pantry/<int:uid>', methods=['GET'])
def get_pantry(uid):
    pantry_ingredients = PantryIngredient.query.filter_by(user_id=uid).all()
    if not pantry_ingredients:
        return jsonify({"message": "No pantry items found for this user."}), 404
    
    ingredients = [item.to_json() for item in pantry_ingredients]
    return jsonify({"pantry": ingredients})

@app.route('/pantry/<int:uid>', methods=['POST'])
def add_pantry_ingredient(uid):
    data = request.json
    ingredient_id = data.get("ingredient_id")
    quantity = data.get("quantity")
    unit = data.get("unit")

    if not ingredient_id or quantity is None or not unit:
        return jsonify({"message": "Please fill out all required fields (ingredient_id, quantity, unit)."}), 400

    new_item = PantryIngredient(user_id=uid, ingredient_id=ingredient_id, quantity=quantity, unit=unit)
    try:
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Ingredient added to pantry!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

@app.route('/pantry/<int:uid>', methods=['PATCH'])
def update_pantry_ingredient(uid):
    data = request.json
    ingredient_id = data.get("ingredient_id")
    quantity = data.get("quantity")
    unit = data.get("unit")

    if not ingredient_id or quantity is None or not unit:
        return jsonify({"message": "Please fill out all required fields (ingredient_id, quantity, unit)."}), 400

    pantry_item = PantryIngredient.query.filter_by(user_id=uid, ingredient_id=ingredient_id).first()
    if not pantry_item:
        return jsonify({"message": "Ingredient not found in pantry."}), 404

    pantry_item.quantity = quantity
    pantry_item.unit = unit
    db.session.commit()
    return jsonify({"message": "Pantry ingredient updated successfully."})

@app.route('/pantry/<int:uid>', methods=['DELETE'])
def remove_pantry_ingredient(uid):
    data = request.json
    ingredient_id = data.get("ingredient_id")

    if not ingredient_id:
        return jsonify({"message": "Please provide the ingredient_id."}), 400

    pantry_item = PantryIngredient.query.filter_by(user_id=uid, ingredient_id=ingredient_id).first()
    if not pantry_item:
        return jsonify({"message": "Ingredient not found in pantry."}), 404

    db.session.delete(pantry_item)
    db.session.commit()
    return jsonify({"message": "Ingredient removed from pantry."})

#Recipe endpoint
@app.route('/recipe', methods=['GET'])
def get_recipes():
    recipes = Recipe.query.all()
    return jsonify([recipe.to_json() for recipe in recipes])



if __name__ == "__main__":
    #with app.app_context():
        #db.create_all()
    app.run(debug=True)


