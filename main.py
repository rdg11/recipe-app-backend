#contains main endpoints CREATE READ UPDATE DELETE
from flask import request, jsonify
from config import app, db
from models import Profiles, Ingredient, PantryIngredient
from sqlalchemy import select

##### profile logic #####

@app.route("/profiles", methods=["GET"])
def get_profiles():
    profiles = Profiles.query.all()
    json_profiles = list(map(lambda x: x.to_json(), profiles))
    return jsonify({"profiles": json_profiles})

@app.route("/create_profile", methods = ["POST"])
def create_profile():
    first_name = request.json.get("firstName")
    last_name = request.json.get("LastName")
    email = request.json.get("email")
    
    if not first_name or not last_name or not email:
        return(
            jsonify({"message": "Please fill out all required fields"}), 400, #first & last name and email
        )
    new_profile = Profiles(first_name = first_name, last_name = last_name, email = email)
    try:
        db.session.add(new_profile)
        db.session.commit()
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    
    return jsonify({"message": "User Created! Welcome!"})


@app.route("/update_profile/int:user_ud>", methods=["PATCH"])
def update_profile(user_id):
    profile = Profiles.query.get(user_id)
    if not profile:
        return jsonify({"message": "User not Found"})
    
    data = request.json
    profile.first_name = data.get("firstName", profile.first_name) #searches key and updates firstname if different from entry there
    profile.last_name = data.get("lastName", profile.last_name)
    profile.email = data.get("email", profile.email)
    
    db.session.commit()
    
    return jsonify({"message": "User Updated!"})

@app.route("/delete_profile/int:user_ud>", methods=["DELETE"])
def delete_profile(user_id):
    profile = Profiles.query.get(user_id)
    if not profile:
        return jsonify({"message": "User not Found"})
    
    db.session.delete(profile)
    db.session.commit()
    
    return jsonify({"message": "User Deleted"})

##### pantry logic #####
@app.route('/pantry', methods=['GET'])
def get_pantry(uid):
    # get all pantry ingredients matching user_id
    pantry_ingredients = db.session.query(PantryIngredient).filter_by(user_id=uid).all()

    # get ingredients matching each pantry_ingredients' associated ingredient_id
    ingredients = []
    for item in pantry_ingredients:
        ingredient = db.session.query(Ingredient).filter_by(ingredient_id=item.ingredient_id).first()
        ingredients.append({
            'ingredient_id': ingredient.id,
            'name': ingredient.name,            
            'quantity': item.quantity,
            'unit': item.unit,
            'contains_nuts': ingredient.contains_nuts,
            'contains_gluten': ingredient.contains_gluten,
            'contains_meat': ingredient.contains_meat,
        })

    # return json of pantry
    return jsonify(ingredients)

@app.route('/pantry', methods=['POST'])
def add_pantry_ingredient(uid):
    # get attributes of pantry ingredient
    ingredientid = request.json.get("ingredient_id")
    qty = request.json.get("quantity")
    munit = request.json.get("unit")

    # test validity
    if not ingredientid or not qty or not munit:
        return(
            jsonify({'message': 'Please fill out all required fields'}), 400, #ingredient id, quantity, unit
        )

    new_item = PantryIngredient(
        user_id=uid,
        ingredient_id=ingredientid,
        quantity=qty,
        unit=munit
    )

    # create new Pantry Ingredient entry
    try:
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'message': 'Ingredient added to pantry!'})

@app.route('/pantry', methods=['PATCH'])
def update_pantry_ingredient(uid):
    # get pantry ingredient attributes
    ingredientid = request.json.get('ingredient_id')
    qty = request.json.get('quantity')
    measurement_unit = request.json.get('unit')

    # test validity
    if not ingredientid or not qty or not measurement_unit:
        return (jsonify({'message': 'Please fill all required fields.'}), 400)
    
    # find pantry item
    pantry_item = db.session.query(PantryIngredient).filter_by(
        user_id=uid, ingredientid=ingredientid
    ).first()
    if not pantry_item:
        return jsonify({'message': 'Ingredient not found in pantry'}), 404
    
    # update fields
    pantry_item.quantity = qty
    pantry_item.unit = measurement_unit
    db.session.commit()

    return jsonify({'message': 'Pantry ingredient updated successfully.'})

@app.route('/pantry', methods=['DELETE'])
def remove_pantry_ingredient(uid):
    # get ingredient id
    ingredientid = request.json.get("ingredient_id")

    if not ingredientid:
        return (jsonify({'message': "Please fill ingredient_id field."}), 400)

    db.session.query(PantryIngredient).filter(user_id=uid, ingredient_id=ingredientid).delete()
    db.session.commit()
    return jsonify({'message': "Ingredient removed from pantry."})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug = True)
