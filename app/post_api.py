from datetime import datetime

from flask import request, jsonify

from app import app, database
from app.api_auth import token_auth
from app.errors import bad_request
from app.models import Post


@app.route('/api/v1/posts/create', methods=['POST'])
@token_auth.login_required
def create_post():
    app.logger.debug(f'Receive request: {request.data}')
    request_data = request.get_json() or {}
    post_text = request_data.get('text')
    if not post_text:
        return bad_request('must include a field "text"')

    post = Post()
    post.text = post_text
    post.user_id = token_auth.current_user().id
    insert_post_query = f"""
    INSERT INTO post (text, creation_timestamp, user_id) 
    VALUES ('{post.text}', '{datetime.utcnow()}', '{post.user_id}') 
    RETURNING post.id
    """
    query_result = database.session.execute(insert_post_query)
    database.session.commit()
    new_post_id = [r for r in query_result][0][0]
    response = jsonify({'post_id': new_post_id})
    response.status_code = 201
    return response
