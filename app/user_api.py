from flask import abort, request, jsonify, url_for

from app import app, database
from app.api_auth import token_auth
from app.api_tools import get_single_json_entity
from app.errors import bad_request, error_response
from app.models import Users


A_USER_QUERY_TEMPLATE = """
SELECT users.id FROM users WHERE users.{} = '{}' LIMIT 1
"""
FULL_USER_QUERY_TEMPLATE = """
SELECT 
users.id, users.username, users.email, users.common_name 
FROM users WHERE users.id = '{}'
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
    response.headers['Location'] = url_for('get_user', user_id=new_user_id)
    return response


@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@token_auth.login_required
def get_user(user_id):
    json_user = get_single_json_entity(
        FULL_USER_QUERY_TEMPLATE.format(user_id)
    )
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
    query = A_USER_QUERY_TEMPLATE.format('id', user_id)
    json_user = get_single_json_entity(query)
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
        name_query = A_USER_QUERY_TEMPLATE.format(
            'username',
            request_data['username']
        )
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
    query = FULL_USER_QUERY_TEMPLATE.format(user_id)
    updated_user = get_single_json_entity(query)
    database.session.commit()
    return jsonify(updated_user)


@app.route('/api/v1/users/<int:user_id>/posts', methods=['GET'])
@token_auth.login_required
def get_user_posts(user_id):
    app.logger.debug(f'Receive request: {request.data}')
    query = A_USER_QUERY_TEMPLATE.format('id', user_id)
    json_user = get_single_json_entity(query)
    if not json_user:
        return error_response(404)

    posts_query = f"""
    SELECT post.id, post.text, post.creation_timestamp, post.user_id FROM post 
    WHERE post.user_id = {user_id} AND post.deleted = FALSE
    """
    query_result_proxy = database.session.execute(posts_query)
    database.session.commit()
    posts = [{k: v for k, v in row.items()} for row in query_result_proxy]
    response = jsonify({'user_posts': posts})
    return response
