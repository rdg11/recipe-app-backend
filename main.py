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
from flask_cors import CORS


db = mysql.connector.connect(
    host= os.environ.get("DB_HOST"),
    user= os.environ.get("DB_USER"),
    password= os.environ.get("DB_PASS"),
    database= os.environ.get("DB_NAME")
) 
cursor = db.cursor()

def get_db_connection():
    """Create a new database connection for each request"""
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASS"),
        database=os.environ.get("DB_NAME"),
        autocommit=False  # We'll handle commits explicitly
    )

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
    
    db = get_db_connection()
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT email, password, user_id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user or not bcrypt.check_password_hash(user["password"], password):
            return jsonify({"message": "Invalid credentials"}), 401
        
        access_token = create_access_token(identity=user["email"])
        return jsonify({"access_token": access_token})
    finally:
        db.close()

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
    try:
        # Create a new connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query to join pantry_ingredient with ingredient to get names
        query = """
        SELECT p.ingredient_id, p.user_id, p.quantity, p.unit, i.name
        FROM pantry_ingredient p
        JOIN ingredient i ON p.ingredient_id = i.ingredient_id
        WHERE p.user_id = %s
        """
        
        cursor.execute(query, (uid,))
        pantry_items = cursor.fetchall()
        
        # Close resources properly
        cursor.close()
        conn.close()
        
        if not pantry_items:
            return jsonify({"message": "No pantry items found for this user.", "pantry": []}), 200
        
        result = []
        for item in pantry_items:
            result.append({
                "ingredientId": item["ingredient_id"],
                "userId": item["user_id"],
                "quantity": float(item["quantity"]) if item["quantity"] is not None else None,
                "unit": item["unit"],
                "ingredient": {"name": item["name"]}
            })
        
        return jsonify({"pantry": result})
        
    except Exception as e:
        print(f"Error in get_pantry: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500

# Update for the backend - in main.py
# Replace update_pantry function with this improved version

@app.route("/update_pantry/<int:uid>", methods=["PATCH"])
@jwt_required()
def update_pantry(uid):
    try:
        data = request.json
        print(f"Received update_pantry request with data: {data}")
        
        added_ingredients = data.get("addedIngredients", [])
        updated_ingredients = data.get("updatedIngredients", [])
        deleted_ingredients = data.get("deletedIngredients", [])

        print(f"Processing {len(added_ingredients)} added, {len(updated_ingredients)} updated, and {len(deleted_ingredients)} deleted ingredients")
        
        # Process added ingredients
        for ingredient in added_ingredients:
            try:
                ingredient_name = ingredient[0]
                quantity = ingredient[1] if ingredient[1] != "" else None
                unit = ingredient[2] if ingredient[2] != "" else ""
                
                print(f"Adding ingredient: {ingredient_name}, {quantity}, {unit}")
                
                # Get a fresh connection for this operation
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                try:
                    # Check if ingredient already exists in database
                    cursor.execute("SELECT ingredient_id FROM ingredient WHERE name = %s", (ingredient_name,))
                    ingredient_obj = cursor.fetchone()
                    
                    if not ingredient_obj:
                        # Create new ingredient
                        cursor.execute(
                            "INSERT INTO ingredient (name, contains_nuts, contains_gluten, contains_meat) VALUES (%s, %s, %s, %s)",
                            (ingredient_name, False, False, False)
                        )
                        conn.commit()
                        ingredient_id = cursor.lastrowid
                        print(f"Created new ingredient with ID: {ingredient_id}")
                    else:
                        ingredient_id = ingredient_obj["ingredient_id"]
                    
                    # Check if ingredient already exists in pantry - use a parameterized query
                    cursor.execute(
                        "SELECT * FROM pantry_ingredient WHERE user_id = %s AND ingredient_id = %s",
                        (uid, ingredient_id)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing entry
                        cursor.execute(
                            "UPDATE pantry_ingredient SET quantity = %s, unit = %s WHERE user_id = %s AND ingredient_id = %s",
                            (quantity, unit, uid, ingredient_id)
                        )
                        print(f"Updated existing pantry item for {ingredient_name}")
                    else:
                        # Add new entry
                        cursor.execute(
                            "INSERT INTO pantry_ingredient (user_id, ingredient_id, quantity, unit) VALUES (%s, %s, %s, %s)",
                            (uid, ingredient_id, quantity, unit)
                        )
                        print(f"Added new pantry item for {ingredient_name}")
                    
                    conn.commit()
                    
                except Exception as e:
                    conn.rollback()
                    print(f"Error processing ingredient {ingredient_name}: {str(e)}")
                    # Continue to next ingredient instead of failing the entire request
                finally:
                    cursor.close()
                    conn.close()
                    
            except Exception as e:
                print(f"Error processing added ingredient {ingredient}: {str(e)}")
                # Continue to next ingredient
        
        # Process updated ingredients
        for ingredient in updated_ingredients:
            try:
                ingredient_name = ingredient[0]
                quantity = ingredient[1] if ingredient[1] != "" else None
                unit = ingredient[2] if ingredient[2] != "" else ""
                
                print(f"Updating ingredient: {ingredient_name}, {quantity}, {unit}")
                
                # Get a fresh connection for this operation
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                try:
                    # Find the ingredient
                    cursor.execute("SELECT ingredient_id FROM ingredient WHERE name = %s", (ingredient_name,))
                    ingredient_obj = cursor.fetchone()
                    
                    if not ingredient_obj:
                        print(f"Ingredient not found: {ingredient_name}")
                        # Skip this ingredient instead of failing the entire request
                        continue
                    
                    ingredient_id = ingredient_obj["ingredient_id"]
                    
                    # Check if ingredient exists in pantry
                    cursor.execute(
                        "SELECT * FROM pantry_ingredient WHERE user_id = %s AND ingredient_id = %s",
                        (uid, ingredient_id)
                    )
                    existing = cursor.fetchone()
                    
                    if not existing:
                        print(f"Ingredient not in pantry: {ingredient_name}")
                        # Skip this ingredient instead of failing
                        continue
                    
                    # Update the entry
                    cursor.execute(
                        "UPDATE pantry_ingredient SET quantity = %s, unit = %s WHERE user_id = %s AND ingredient_id = %s",
                        (quantity, unit, uid, ingredient_id)
                    )
                    
                    conn.commit()
                    
                except Exception as e:
                    conn.rollback()
                    print(f"Error updating ingredient {ingredient_name}: {str(e)}")
                    # Continue to next ingredient
                finally:
                    cursor.close()
                    conn.close()
                
            except Exception as e:
                print(f"Error processing updated ingredient {ingredient}: {str(e)}")
                # Continue to next ingredient
        
        # Process deleted ingredients - one at a time with separate connections
        for ingredient_name in deleted_ingredients:
            try:
                print(f"Deleting ingredient: {ingredient_name}")
                
                # Get a fresh connection for this operation
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                try:
                    # Use a JOIN to make sure we only delete the right ingredient
                    delete_query = """
                    DELETE p FROM pantry_ingredient p
                    JOIN ingredient i ON p.ingredient_id = i.ingredient_id
                    WHERE p.user_id = %s AND i.name = %s
                    """
                    
                    cursor.execute(delete_query, (uid, ingredient_name))
                    
                    if cursor.rowcount > 0:
                        print(f"Successfully deleted {ingredient_name}")
                    else:
                        print(f"No matching pantry item found for {ingredient_name}")
                    
                    conn.commit()
                    
                except Exception as e:
                    conn.rollback()
                    print(f"Error deleting ingredient {ingredient_name}: {str(e)}")
                finally:
                    cursor.close()
                    conn.close()
                
            except Exception as e:
                print(f"Error processing deleted ingredient {ingredient_name}: {str(e)}")
                # Continue to next ingredient
        
        return jsonify({"message": "Successfully updated pantry."})
        
    except Exception as e:
        print(f"Error in update_pantry: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500


@app.route("/save_recipe/<int:uid>", methods=["POST"])
@jwt_required()
def save_recipe(uid):
    data = request.json
    recipe_data = data.get("recipe")
    
    if not recipe_data:
        return jsonify({"message": "No recipe data provided"}), 400
    
    # Create the recipe
    new_recipe = Recipe(
        name=recipe_data.get("recipeName"),
        description=recipe_data.get("description"),
        steps=json.dumps(recipe_data.get("steps")),
        is_vegetarian=recipe_data.get("allergyFlags", {}).get("containsVegetarian", False),
        is_gluten_free=not recipe_data.get("allergyFlags", {}).get("containsGluten", False),
        is_nut_free=not recipe_data.get("allergyFlags", {}).get("containsNuts", False)
    )
    
    db.session.add(new_recipe)
    db.session.commit()
    
    # Add ingredients
    ingredients_list = recipe_data.get("ingredients", "").split(", ")
    for ingredient_name in ingredients_list:
        # Check if ingredient exists
        ingredient = Ingredient.query.filter_by(name=ingredient_name).first()
        if not ingredient:
            # Create new ingredient
            ingredient = Ingredient(
                name=ingredient_name,
                contains_nuts=False,  # Default values, can be updated later
                contains_gluten=False,
                contains_meat=False
            )
            db.session.add(ingredient)
            db.session.commit()
        
        # Create recipe ingredient relationship
        recipe_ingredient = RecipeIngredient(
            recipe_id=new_recipe.recipe_id,
            ingredient_id=ingredient.ingredient_id,
            quantity=1.0,  # Default values, can be updated later
            unit="unit"
        )
        db.session.add(recipe_ingredient)
    
    db.session.commit()
    
    # Add to user favorites
    user_favorite = UserFavoriteRecipe(
        user_id=uid,
        recipe_id=new_recipe.recipe_id
    )
    db.session.add(user_favorite)
    db.session.commit()
    
    return jsonify({"message": "Recipe saved successfully", "recipe_id": new_recipe.recipe_id}), 201

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
    
    # Get the user from the database using the JWT identity (email)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Find the user ID from the email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (current_user_email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        user_id = user["user_id"]
        
        # Get the pantry ingredients for this user using the existing query
        query = """
        SELECT p.ingredient_id, p.user_id, p.quantity, p.unit, i.name
        FROM pantry_ingredient p
        JOIN ingredient i ON p.ingredient_id = i.ingredient_id
        WHERE p.user_id = %s
        """
        
        cursor.execute(query, (user_id,))
        pantry_items = cursor.fetchall()
        
        # Format ingredients for the AI with consistent formatting
        ingredients_list = []
        for item in pantry_items:
            # Format quantity if it exists
            if item['quantity'] is not None and item['unit']:
                ingredients_list.append(f"{item['name']} ({float(item['quantity'])} {item['unit']})")
            elif item['quantity'] is not None:
                ingredients_list.append(f"{item['name']} ({float(item['quantity'])})")
            else:
                ingredients_list.append(item['name'])
        
        # Join ingredients into a comma-separated string
        ingredients = ", ".join(ingredients_list) if ingredients_list else ""
        
        print(f"User query: {user_query}")
        print(f"Ingredients from pantry: {ingredients}")
        
        # Generate recipes using the ingredients and user query
        result = generate_recipes_from_ingredients(user_query, ingredients)
        
        # Additional verification of results to ensure matching with pantry
        if 'recipes' in result:
            pantry_items_lower = [item['name'].lower() for item in pantry_items]
            
            for recipe in result['recipes']:
                if 'missingIngredients' in recipe and recipe['missingIngredients']:
                    # Clean up and verify missing ingredients
                    missing_ingredients = []
                    for missing in recipe['missingIngredients'].split(','):
                        missing_item = missing.strip().lower()
                        # Only keep as missing if truly not in pantry
                        if not any(pantry_item in missing_item or missing_item in pantry_item 
                                  for pantry_item in pantry_items_lower):
                            missing_ingredients.append(missing.strip())
                    
                    # Update missing ingredients list
                    recipe['missingIngredients'] = ", ".join(missing_ingredients)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in recipe generation: {str(e)}")
        return jsonify({"message": f"Server error: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()


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