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

INSERT INTO users (first_name, last_name, email, is_vegetarian, is_nut_free, is_gluten_free)
VALUES ('John', 'Doe', 'john.doe@example.com', TRUE, FALSE, TRUE);

SELECT * FROM users;


