#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        try:
            if not json.get('username') or not json.get('password'):
                return {'errors': ['validation errors']}, 422
            
            user = User(
                username=json['username'],
                image_url=json.get('image_url'),
                bio=json.get('bio')
            )
            user.password_hash = json['password']
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except (IntegrityError, ValueError) as e:
            return {'errors': ['validation errors']}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict()
        return {'error': 'Unauthorized'}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username == json['username']).first()
        if user and user.authenticate(json['password']):
            session['user_id'] = user.id
            return user.to_dict()
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return '', 204
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        if not data.get("title"):
            return {"error": "Title is required"}, 422
        if not data.get("instructions") or len(data["instructions"]) < 50:
            return {"error": "Instructions must be at least 50 characters"}, 422
        if not isinstance(data.get("minutes_to_complete"), int):
            return {"error": "Minutes to complete must be an integer"}, 422

        recipe = Recipe(
            title=data["title"],
            instructions=data["instructions"],
            minutes_to_complete=data["minutes_to_complete"],
            user_id=user_id
        )
        db.session.add(recipe)
        db.session.commit()

        return recipe.to_dict(), 201
api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")
