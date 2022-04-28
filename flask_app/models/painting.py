from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_app.models import user

class Painting:
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.price = data['price']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.user = None

    @classmethod
    def save(cls, data):
        query = 'INSERT INTO paintings ( title, description, price, user_id, created_at, updated_at ) VALUES ( %(title)s, %(description)s, %(price)s, %(user_id)s, NOW(), NOW() );'
        results = connectToMySQL('paintings').query_db(query, data)
        return results

    @classmethod
    def update(cls, data):
        query = 'UPDATE paintings SET title = %(title)s, description = %(description)s, price = %(price)s, updated_at = NOW() WHERE id = %(id)s;'
        return connectToMySQL('paintings').query_db(query, data)

    @classmethod
    def delete(cls, data):
        query = 'DELETE FROM paintings WHERE id = %(id)s;'
        return connectToMySQL('paintings').query_db(query, data)

    @classmethod
    def get_painting_by_id(cls, data):
        query = 'SELECT * FROM paintings WHERE id = %(id)s;'
        results = connectToMySQL('paintings').query_db(query, data)
        return cls( results[0] )

    @classmethod
    def get_all_paintings(cls):
        query = 'SELECT * FROM paintings;'
        results = connectToMySQL('paintings').query_db(query)
        all_paintings = []
        for row in results:
            all_paintings.append( cls(row) )
        return all_paintings

    @classmethod
    def get_all_paintings_with_users(cls):
        query = 'SELECT * FROM paintings JOIN users ON users.id = paintings.user_id;'
        results = connectToMySQL('paintings').query_db(query)
        if len(results) < 1:
            return None
        else:
            all_paintings = []
            for each_painting in results:
                this_painting_instance = cls(each_painting)
                this_user_dictionary = {
                    "id": each_painting['users.id'],
                    "first_name": each_painting['first_name'],
                    "last_name": each_painting['last_name'],
                    "email": each_painting['email'],
                    "password": each_painting['password'],
                    "created_at": each_painting['users.created_at'],
                    "updated_at": each_painting['users.updated_at']
                }
                painting_creator = user.User(this_user_dictionary)
                this_painting_instance.user = painting_creator
                all_paintings.append(this_painting_instance)
            return all_paintings

    @classmethod
    def get_one_painting_with_user(cls, data):
        query = 'SELECT * FROM paintings JOIN users ON users.id = paintings.user_id WHERE paintings.id = %(id)s;'
        results = connectToMySQL('paintings').query_db(query, data)
        if len(results) < 1:
            return None
        else:
            one_painting = cls(results[0])
            this_user_dictionary = {
                "id": results[0]['users.id'],
                "first_name": results[0]['first_name'],
                "last_name": results[0]['last_name'],
                "email": results[0]['email'],
                "password": results[0]['password'],
                "created_at": results[0]['users.created_at'],
                "updated_at": results[0]['users.updated_at']
            }
            painting_creator = user.User(this_user_dictionary)
            one_painting.user = painting_creator
            return one_painting


    @classmethod
    def get_user_paintings(cls, data):
        query = "SELECT * FROM users LEFT JOIN paintings ON users.id = paintings.user_id;"
        results = connectToMySQL('paintings').query_db(query,data)
        paintings = []
        for painting in results:
            paintings.append( cls(painting) )
        return paintings

    @staticmethod
    def validate_painting(painting):
        is_valid = True
        if len(painting['title']) < 2:
            flash('Title should be at least 2 characters long', 'painting')
            is_valid = False
        if len(painting['description']) < 10:
            flash('Description should be at least 10 characters long', 'painting')
            is_valid = False
        price_str = painting['price']
        if price_str is '':
            flash('Price should be greater than 0', 'painting')
            is_valid = False
        elif int(price_str) < 1:
            flash('Price should be greater than 0', 'painting')
            is_valid = False
        return is_valid