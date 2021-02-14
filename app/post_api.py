from datetime import datetime

from flask import abort, request, jsonify, url_for

from app import app, database
from app.api_auth import token_auth
from app.api_tools import get_single_json_entity
from app.errors import bad_request, error_response


SINGLE_POST_QUERY_TEMPLATE = """
    SELECT 
    post.id, post.text, post.creation_timestamp, post.user_id 
    FROM post WHERE post.id = '{}' AND post.deleted = FALSE
    """


@app.route('/api/v1/posts/create', methods=['POST'])
@token_auth.login_required
def create_post():
    app.logger.debug(f'Receive request: {request.data}')
    request_data = request.get_json() or {}
    post_text = request_data.get('text')
    if not post_text:
        return bad_request('must include a field "text"')

    author_id = token_auth.current_user().id
    insert_post_query = f"""
    INSERT INTO post (text, creation_timestamp, user_id, deleted) 
    VALUES ('{post_text}', '{datetime.utcnow()}', '{author_id}', FALSE) 
    RETURNING post.id
    """
    query_result = database.session.execute(insert_post_query)
    database.session.commit()
    new_post_id = [r for r in query_result][0][0]
    response = jsonify({'post_id': new_post_id})
    response.status_code = 201
    response.headers['Location'] = url_for('get_post', post_id=new_post_id)
    return response


@app.route('/api/v1/posts/<int:post_id>', methods=['GET'])
@token_auth.login_required
def get_post(post_id):
    post_query = SINGLE_POST_QUERY_TEMPLATE.format(post_id)
    json_post = get_single_json_entity(post_query)
    if json_post:
        response = jsonify(json_post)
    else:
        response = error_response(404)
    return response


@app.route('/api/v1/posts/<int:post_id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(post_id):
    post_query = SINGLE_POST_QUERY_TEMPLATE.format(post_id)
    json_post = get_single_json_entity(post_query)
    if not json_post:
        return error_response(404)
    if token_auth.current_user().id != json_post['user_id']:
        abort(403)

    delete_post_query = f"""
    UPDATE post SET deleted = TRUE WHERE post.id = '{post_id}'
    """
    database.session.execute(delete_post_query)
    database.session.commit()
    response = jsonify({'status': "OK"})
    return response

