#contains main endpoints CREATE READ UPDATE DELETE
from flask import request, jsonify
from config import app, db
from models import Profiles

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug = True)
