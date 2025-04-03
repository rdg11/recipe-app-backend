# recipe-app-backend

python api

# Dependencies

Install all dependencies with: pip install -r requirements.txt
- alembic
- Flask
- flask_bcrypt
- flask_cors
- flask_jwt_extended
- Flask_Migrate
- flask_sqlalchemy
- mysql_connector_python
- PyMySQL
- python-dotenv
- SQLAlchemy

When running for the first time to set up database (with migration folder)
-  flask --app main db upgrade
-  OR  flask --app main db upgrade > output.txt 2>&1 (to display to file)

To test connection:
- flask --app main run
- curl http://localhost:5000/users

To add a user for testing with SQL (can also do a POST request from terminal):

- mysql -u your_username -p
- P@ssw0rd!
- USE four_eleven;

Example code and guides for accomplishing common tasks with the OpenAI API. To run these examples, you'll need an OpenAI account and associated API key (create a free account here). Set an environment variable called OPENAI_API_KEY with your API key. Alternatively, in most IDEs such as Visual Studio Code, you can create an .env file at the root of your repo containing OPENAI_API_KEY=<your API key>, which will be picked up by the notebooks.
Most code examples are written in Python, though the concepts can be applied in any language

INSERT INTO users (first_name, last_name, email, is_vegetarian, is_nut_free, is_gluten_free)
VALUES ('John', 'Doe', 'john.doe@example.com', TRUE, FALSE, TRUE);

SELECT * FROM users;


