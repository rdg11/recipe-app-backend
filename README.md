# recipe-app-backend

python api


# Dependencies
- SQLAlchemy
- flask
- Flask-SQLALCHEMY
- flask-cors

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


