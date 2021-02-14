import base64
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

from app import database


SECONDS_PER_DAY = 86400


class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(64), index=True, unique=True)
    common_name = database.Column(database.String(64), index=True)
    email = database.Column(database.String(120), index=True)
    password_hash = database.Column(database.String(128))
    token = database.Column(database.String(32), index=True, unique=True)
    token_expiration = database.Column(database.DateTime)
    posts = database.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'common_name']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=SECONDS_PER_DAY):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        update_token_query = f"""
        UPDATE users 
        SET token='{self.token}', token_expiration='{self.token_expiration}'
        WHERE users.id = '{self.id}'
        """
        database.session.execute(update_token_query)
        return self.token

    @staticmethod
    def check_token(token):
        user = Users.query.filter_by(token=token).first()
        print(f'Find a token {token} for user {user}')
        if user is None or user.token_expiration < datetime.utcnow():
            print(f'Invalid token')
            return None
        return user


class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    text = database.Column(database.String(1000))
    creation_timestamp = database.Column(
        database.DateTime,
        index=True,
        default=datetime.utcnow
    )
    user_id = database.Column(
        database.Integer,
        database.ForeignKey('users.id')
    )

    def __repr__(self):
        return '<Post {}>'.format(self.body)
