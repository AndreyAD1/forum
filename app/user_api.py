from flask import request, jsonify

from app import app, database
from app.errors import bad_request, error_response
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
    query_result = database.session.execute(insert_command)
    database.session.commit()
    new_user_id = [r for r in query_result][0][0]
    response = jsonify({'user_id': new_user_id})
    response.status_code = 201
    return response


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user_query = f"""SELECT users.id, users.username, users.email 
    FROM users WHERE users.id = '{user_id}'
    """
    query_result_proxy = database.session.execute(user_query)
    row_proxies = [r for r in query_result_proxy]
    if len(row_proxies) == 1:
        response = jsonify({k: v for k, v in row_proxies[0].items()})
    else:
        response = error_response(404)

    return response
