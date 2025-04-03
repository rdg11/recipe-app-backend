import os
import json
from openai import OpenAI
import mysql.connector

def generate_recipes_from_ingredients(user_query,ingredients):
    """
    Connect to OpenAI API and generate recipe suggestions based on the provided ingredients.
    Args:
        ingredients_list (list): List of food ingredients
    Returns:
        dict: The recipe suggestions
    """
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    # Format the ingredients as a comma-separated string
    #ingredients_str = ", ".join(ingredients_list)
    # Create the prompt
    prompt = f"""
    I have the following ingredients:
    {ingredients}
    {user_query}
    Please provide three recipes:
    1. The name of each recipe
    2. A brief description
    3. Step-by-step cooking instructions
    4. Which of my ingredients will be used
    5. Any essential ingredients I might be missing
    Format your response as a JSON object with an array of recipe objects.
    """
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful cooking assistant. You suggest recipes based on available ingredients and return your response in JSON format. Assume salt and pepper are generally available."},
            {"role": "user", "content": prompt}
        ]
    )
    # Parse the response
    try:
        recipes_json = json.loads(response.choices[0].message.content)
        return recipes_json
    except json.JSONDecodeError:
        return {"error": "Failed to parse the response as JSON", "raw_content": response.choices[0].message.content}

def getListOfIngredients(username):
    #connect to database, select query to get ingredients for particular user
    try:
        db = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            database=os.environ.get("DB_NAME")
        )
        cursor = db.cursor()
        query = """select i.name from pantry_ingredient p 
        inner join users u on u.user_id	= p.user_id
        inner join ingredient i on p.ingredient_id = i.ingredient_id
        where u.email = %s
"""
        parameters = (username, )
        cursor.execute(query, parameters)
        rows = cursor.fetchall()
        ingredients = [row[0] for row in rows]
        return ingredients

    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return []

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()