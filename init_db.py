from config import app, db
from models import User, Ingredient, PantryIngredient, Recipe, RecipeIngredient, Review, UserFavoriteRecipe
import os
import pymysql

# Print environment variables for debugging
print(f"DB_USER: {os.environ.get('DB_USER')}")
print(f"DB_HOST: {os.environ.get('DB_HOST')}")
print(f"DB_NAME: {os.environ.get('DB_NAME')}")

# Create the database if it doesn't exist
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME", "four_eleven")

# Connect without specifying a database
try:
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass
    )
    
    with connection.cursor() as cursor:
        # Create the database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists")
    
    connection.close()
except Exception as e:
    print(f"Error creating database: {e}")

# Now create the tables
with app.app_context():
    # Create all tables from scratch
    db.create_all()
    print("Database tables created successfully!")