from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates   # <-- ADD THIS LINE
from werkzeug.security import generate_password_hash, check_password_hash
from config import db

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=False, default=generate_password_hash("default123"))
    image_url = db.Column(db.String, default="")
    bio = db.Column(db.String, default="")


    recipes = db.relationship(
        "Recipe",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    serialize_rules = ("-recipes.user", "-_password_hash")

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = generate_password_hash(password)

    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("User", back_populates="recipes")

    @validates("instructions")
    def validate_instructions(self, key, instructions):
        if instructions is None or len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return instructions
