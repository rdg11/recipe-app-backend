from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

# Get database connection from environment variables
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_host = os.environ.get("DB_HOST")
db_name = os.environ.get("DB_NAME", "four_eleven")

# Construct the connection string
db_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"

# Use RDS database if environment variables exist, otherwise use local
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri if all([db_user, db_pass, db_host]) else "mysql+pymysql://root:H0ck3y71@127.0.0.1/four_eleven"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)