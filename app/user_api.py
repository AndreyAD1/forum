from flask import request, jsonify

from app import app, database
from app.errors import bad_request
from app.models import Users


@app.route('/api/v1/users/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if Users.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if Users.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = Users()
    user.from_dict(data, new_user=True)
    insert_template = "INSERT INTO users (username, email, password_hash) VALUES ('{}', '{}', '{}') RETURNING users.id"
    insert_command = insert_template.format(
        user.username,
        user.email,
        user.password_hash
    )
    database.session.execute(insert_command)
    database.session.commit()
    response = jsonify({})
    response.status_code = 201
    return response
