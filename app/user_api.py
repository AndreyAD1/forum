from flask import abort, request, jsonify, url_for

from app import app, database
from app.api_auth import token_auth
from app.errors import bad_request, error_response
from app.models import Users


A_USER_QUERY_TEMPLATE = """
SELECT users.id FROM users WHERE users.{} = '{}' LIMIT 1
"""


@app.route('/api/v1/users/create', methods=['POST'])
def create_user():
    app.logger.debug(f'Receive request: {request.data}')
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')

    name_query = A_USER_QUERY_TEMPLATE.format('username', data['username'])
    query_result_proxy = database.session.execute(name_query)
    query_result = [r for r in query_result_proxy]
    if query_result:
        return bad_request('please use a different username')

    user = Users()
    user.from_dict(data, new_user=True)
    insert_command = f"""
    INSERT INTO users (username, email, common_name, password_hash) 
    VALUES (
    '{user.username}', '{user.email}', '{user.common_name}',
    '{user.password_hash}'
    ) 
    RETURNING users.id
    """
    query_result = database.session.execute(insert_command)
    database.session.commit()
    new_user_id = [r for r in query_result][0][0]
    response = jsonify({'user_id': new_user_id})
    response.status_code = 201
    return response


def get_json_user(user_id):
    user_query = f"""
    SELECT 
    users.id, users.username, users.email, users.common_name 
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
@token_auth.login_required
def get_user(user_id):
    json_user = get_json_user(user_id)
    if json_user:
        response = jsonify(json_user)
    else:
        response = error_response(404)
    return response


@app.route('/api/v1/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def update_user(user_id):
    if token_auth.current_user().id != user_id:
        abort(403)

    json_user = get_json_user(user_id)
    if not json_user:
        return error_response(404)
    request_data = request.get_json() or {}

    mutable_field_names = ['username', 'email', 'common_name']
    fields_to_update = {
        k: v for k, v in request_data.items() if k in mutable_field_names
    }
    if not fields_to_update:
        return bad_request('must include username, email or common_name')

    if 'username' in fields_to_update:
        name_query = A_USER_QUERY_TEMPLATE.format('username', request_data['username'])
        query_result_proxy = database.session.execute(name_query)
        new_username_is_not_unique = bool([r for r in query_result_proxy])
        if new_username_is_not_unique:
            return bad_request(f'please use a different username')

    update_query_template = "UPDATE users SET {} WHERE users.id = {}"
    updating_set = ','.join(
        [f"{f} = '{v}'" for f, v in fields_to_update.items()]
    )
    update_query = update_query_template.format(updating_set, user_id)
    database.session.execute(update_query)
    updated_user = get_json_user(user_id)
    database.session.commit()
    return jsonify(updated_user)
