import os
import json
from openai import OpenAI
import mysql.connector

def generate_recipes_from_ingredients(user_query, ingredients):
    """
    Connect to OpenAI API and generate recipe suggestions based on the provided ingredients.
    Args:
        user_query (str): User's query or preferences for recipes
        ingredients (str): Comma-separated string of food ingredients from the user's pantry
    Returns:
        dict: The recipe suggestions with proper structure
    """
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Parse and normalize the ingredients list for better matching
    pantry_items = []
    if ingredients:
        # Split the ingredients string and clean up each item
        for item in ingredients.split(','):
            # Extract just the ingredient name (without quantity/unit in parentheses)
            clean_item = item.strip()
            if '(' in clean_item:
                clean_item = clean_item.split('(')[0].strip()
            pantry_items.append(clean_item.lower())
    
    # Create the prompt with emphasis on accurate pantry ingredient usage
    prompt = f"""
    I have the following ingredients in my pantry:
    {ingredients}
    
    My recipe request: {user_query}
    
    Please provide three recipes that maximize the use of my pantry ingredients. Pay careful attention to the following:
    
    1. ONLY list ingredients as "missing" if they are truly not in my pantry list above.
    2. Be precise - if I have "steak" in my pantry, don't list "steak" as missing.
    3. Normalized pantry ingredients (for your reference): {', '.join(pantry_items)}
    
    For each recipe include:
    1. The name of each recipe (recipeName)
    2. A brief description (description)
    3. Step-by-step cooking instructions (steps as an array)
    4. Which of my pantry ingredients will be used (ingredients as a comma-separated string)
    5. Any essential ingredients I might be missing (missingIngredients as a comma-separated string) - ONLY include ingredients NOT in my pantry
    6. An estimated preparation time (prepTime as a string like "20 min" or "1 hour 15 min")
    7. Allergy and dietary flags in an allergyFlags object with these properties:
       - containsVegetarian: true ONLY if the dish is truly vegetarian (no meat, poultry, or fish)
       - containsGluten: true if the dish contains gluten (wheat, barley, rye, etc.)
       - containsNuts: true if the dish contains nuts of any kind
       - containsMeat: true if the dish contains any meat, poultry, or fish
    
    Be very accurate with the dietary flags. For example, a steak recipe should have containsVegetarian: false and containsMeat: true.
    
    Format your response as a JSON object with a 'recipes' key containing an array of recipe objects with the structure shown above.
    """
    
    # Make the API call
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful cooking assistant. You suggest recipes based on available ingredients in the user's pantry and return your response in JSON format. Assume salt and pepper are generally available. Always include a 'recipes' key in your response containing an array of recipe objects. Be extremely accurate about which ingredients are missing versus available in the pantry."},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Parse the response
    try:
        recipes_json = json.loads(response.choices[0].message.content)
        
        # Ensure the response has the expected structure
        if 'recipes' not in recipes_json:
            # If OpenAI didn't return with a 'recipes' key, adapt the structure
            if isinstance(recipes_json, dict) and any(key in recipes_json for key in ['recipe', 'Recipe', 'recipeList', 'results']):
                for key in ['recipe', 'Recipe', 'recipeList', 'results']:
                    if key in recipes_json and isinstance(recipes_json[key], list):
                        return {"recipes": recipes_json[key]}
            
            # If we have an array of recipes at the top level
            if isinstance(recipes_json, dict) and any(isinstance(recipes_json.get(key), list) for key in recipes_json):
                for key, value in recipes_json.items():
                    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                        return {"recipes": value}
            
            # Last resort: wrap the entire response in a recipes key
            return {"recipes": [recipes_json] if isinstance(recipes_json, dict) else []}
        
        return recipes_json
        
    except json.JSONDecodeError:
        return {"recipes": [], "error": "Failed to parse the response as JSON", "raw_content": response.choices[0].message.content}

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