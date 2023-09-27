from flask import Flask, jsonify, request, render_template,session,redirect,Response
import pymongo
import json
from bson import json_util
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId


myclient = pymongo.MongoClient("mongodb+srv://team17:TqZI3KaT56q6xwYZ@team17.ufycbtt.mongodb.net/")
mydb = myclient.test

class User:

    def start_session(self, user):
        del user['password']
        user_json = json_util.dumps(user)
        session['logged_in'] = True
        session['user'] = user_json
        return user_json

    def signup(self):

        if request.form.get('password') != request.form.get('password_confirm'):
            return jsonify({ "error": "Confirm Password must match"}), 401

        user = {
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
            "gender": request.form.get('gender'),
            "birthday": request.form.get('birthday')
        }
        user['password'] = pbkdf2_sha256.encrypt(user['password'])

        user_json = json_util.dumps(user)

        if not mydb.users.find_one({ "email": user['email']}):
            mydb.users.insert_one(user)
            return self.start_session(user)

        elif mydb.users.find_one({ "email": user['email']}): 
            return jsonify({ "error": "email address already exist"}), 400

        else:
            return jsonify({ "error": "something's wrong..."}), 400

        '''
        #checking for existing email
        if mydb.users.find_one({ "email": user['email']}):
           return jsonify({ "error": "email address already exist"}), 400
        
        if mydb.users.insert_one(user):

            return self.start_session(user)
        
        return jsonify({"error": "sign up error"}), 400
        '''

    def signout(self):
        session.clear()
        return redirect('/')
    
    def login(self):
        user = mydb.users.find_one({
            "email": request.form.get('email')
        })

        if not user:
            return jsonify({ "error": "email not found"}), 401

        elif not pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return jsonify({ "error": "password incorrect"}), 401

        elif user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
            return self.start_session(user)
        
        return jsonify({ "error": "Something's wrong..." }), 401
        #return jsonify({ "error": "Invalid" }), 401
       
    def update_user(self):
        user_json = session.get('user')  # Get user JSON from session
        user_data = json.loads(user_json)  # Parse JSON to dictionary
        user_email = user_data['email']
        
        
        if not user_email:
            return jsonify({"error": "Email not found in session"}), 400
        
        update_data = {
            "name": request.form.get('name'),
            "password": pbkdf2_sha256.encrypt(request.form.get('password')),
            "phone": request.form.get('phone'),
            "address": request.form.get('address'),
            "gender": request.form.get('gender'),
            "birthday": request.form.get('birthday')
        }
        for field in ['name', 'phone', 'address', 'gender', 'birthday']:
            new_value = request.form.get(field)
            if new_value:
                update_data[field] = new_value

        # Handle password separately to hash it before updating
        new_password = request.form.get('password')
        if new_password:
            update_data['password'] = pbkdf2_sha256.encrypt(new_password)
        
        if not update_data:
            return jsonify({"error": "No fields to update"}), 400

        # Update the user information
        result = mydb.users.update_one(
            {"email": user_email},
            {"$set": update_data}            
        )

        if result.modified_count > 0:
            # Fetch and return the updated user
            updated_user = mydb.users.find_one({"email": user_email})
            del updated_user['password']
            
            # Update the session with the new user data
            session['user'] = json_util.dumps(updated_user)
            
            return json_util.dumps(updated_user)
        
        return jsonify({"error": "Update failed"}), 400

