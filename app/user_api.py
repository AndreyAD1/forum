from flask import request, jsonify

from app import app, database
from app.errors import bad_request, error_response
from app.models import Users


A_USER_QUERY_TEMPLATE = """
SELECT users.id FROM users WHERE users.{} = '{}' LIMIT 1
"""


@app.route('/api/v1/users/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')

    name_query = A_USER_QUERY_TEMPLATE.format('username', data['username'])
    query_result_proxy = database.session.execute(name_query)
    query_result = [r for r in query_result_proxy]
    if query_result:
        return bad_request('please use a different username')

    email_query = A_USER_QUERY_TEMPLATE.format('email', data['email'])
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


def get_json_user(user_id):
    user_query = f"""SELECT users.id, users.username, users.email 
    FROM users WHERE users.id = '{user_id}'
    """
    query_result_proxy = database.session.execute(user_query)
    row_proxies = [r for r in query_result_proxy]
    if len(row_proxies) == 1:
        json_user = {k: v for k, v in row_proxies[0].items()}
    else:
        json_user = {}

    return json_user


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    json_user = get_json_user(user_id)
    if json_user:
        response = jsonify(json_user)
    else:
        response = error_response(404)
    return response


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    json_user = get_json_user(user_id)
    if not json_user:
        return error_response(404)
    data = request.get_json() or {}

    fields_to_update = []
    for field_name in ['username', 'email']:
        if field_name in data:
            name_query = A_USER_QUERY_TEMPLATE.format(
                field_name,
                data[field_name]
            )
            query_result_proxy = database.session.execute(name_query)
            new_username_is_not_unique = bool([r for r in query_result_proxy])
            if new_username_is_not_unique:
                return bad_request(f'please use a different {field_name}')
            fields_to_update.append((field_name, data[field_name]))

    update_query_template = "UPDATE users SET {} WHERE users.id = {}"
    updating_set = ','.join([f"{f} = '{v}'" for f, v in fields_to_update])
    update_query = update_query_template.format(updating_set, user_id)
    database.session.execute(update_query)
    database.session.commit()
    return jsonify({})
