from flask import request, jsonify, url_for

from app import app, database
from app.api_auth import token_auth
from app.api_tools import get_single_json_entity
from app.errors import bad_request, error_response


A_FORUM_QUERY_TEMPLATE = """
SELECT forum.id FROM forum WHERE forum.{} = '{}' LIMIT 1
"""
FULL_FORUM_QUERY_TEMPLATE = """
SELECT 
forum.id, forum.name, forum.short_name, forum.creator_id 
FROM forum WHERE forum.id = '{}'
"""


@app.route('/api/v1/forums/create', methods=['POST'])
@token_auth.login_required
def create_forum():
    app.logger.debug(f'Receive request: {request.data}')
    request_data = request.get_json() or {}
    if 'name' not in request_data or 'short_name' not in request_data:
        return bad_request('must include name amd short_name fields')

    for unique_field_name in ['name', 'short_name']:
        forum_query = A_FORUM_QUERY_TEMPLATE.format(
            unique_field_name,
            request_data[unique_field_name],
        )
        query_result_proxy = database.session.execute(forum_query)
        query_result = [r for r in query_result_proxy]
        if query_result:
            return bad_request(f'please use a different {unique_field_name}')

    creator_id = token_auth.current_user().id
    insert_command = f"""
    INSERT INTO forum (name, short_name, creator_id) 
    VALUES (
    '{request_data['name']}', '{request_data['short_name']}', '{creator_id}'
    ) 
    RETURNING forum.id
    """
    query_result = database.session.execute(insert_command)
    database.session.commit()
    new_forum_id = [r for r in query_result][0][0]
    response = jsonify({'forum_id': new_forum_id})
    response.status_code = 201
    response.headers['Location'] = url_for('get_forum', forum_id=new_forum_id)
    return response


@app.route('/api/v1/forums/<int:forum_id>', methods=['GET'])
@token_auth.login_required
def get_forum(forum_id):
    json_forum = get_single_json_entity(
        FULL_FORUM_QUERY_TEMPLATE.format(forum_id)
    )
    if json_forum:
        response = jsonify(json_forum)
    else:
        response = error_response(404)
    return response


@app.route('/api/v1/forums/<int:forum_id>/threads', methods=['GET'])
@token_auth.login_required
def get_forum_threads(forum_id):
    app.logger.debug(f'Receive request: {request.data}')
    query = A_FORUM_QUERY_TEMPLATE.format('id', forum_id)
    json_forum = get_single_json_entity(query)
    if not json_forum:
        return error_response(404)

    threads_query = f"""
    SELECT * FROM thread 
    WHERE thread.forum_id = {forum_id} AND thread.deleted = FALSE
    """
    query_result_proxy = database.session.execute(threads_query)
    database.session.commit()
    threads = [{k: v for k, v in row.items()} for row in query_result_proxy]
    response = jsonify({'forum_threads': threads})
    return response
