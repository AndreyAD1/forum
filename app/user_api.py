from flask import request, jsonify

from app import app, database
from app.errors import bad_request
from app.models import Users


@app.route('/api/v1/users/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    name_query = f"""
    SELECT users.id
    FROM users WHERE users.username = '{data['username']}' LIMIT 1
    """
    query_result_proxy = database.session.execute(name_query)
    query_result = [r for r in query_result_proxy]
    if query_result:
        return bad_request('please use a different username')

    email_query = f"""
    SELECT users.id
    FROM users WHERE users.email = '{data['email']}' LIMIT 1
    """
    query_result_proxy = database.session.execute(email_query)
    query_result = [r for r in query_result_proxy]
    if query_result:
        return bad_request('please use a different email address')

    user = Users()
    user.from_dict(data, new_user=True)
    insert_command = f"""
    INSERT INTO users (username, email, password_hash) 
    VALUES ('{user.username}', '{user.email}', '{user.password_hash}') 
    RETURNING users.id
    """
    database.session.execute(insert_command)
    database.session.commit()
    response = jsonify({})
    response.status_code = 201
    return response
