from datetime import datetime

from flask import abort, request, jsonify, url_for

from app import app, database
from app.api_auth import token_auth
from app.api_tools import get_single_json_entity
from app.errors import bad_request, error_response
from app.models import Thread


SINGLE_THREAD_QUERY_TEMPLATE = """
    SELECT 
    thread.id, thread.name, thread.short_name, thread.creator_id,
    thread.creation_timestamp, thread.text, thread.forum_id
    FROM thread WHERE thread.id = '{}' AND thread.deleted = FALSE
    """


@app.route('/api/v1/threads/create', methods=['POST'])
@token_auth.login_required
def create_thread():
    app.logger.debug(f'Receive request: {request.data}')
    request_data = request.get_json() or {}

    if 'forum_id' not in request_data:
        bad_request('must include a forum_id')

    all_column_names = Thread.__table__.columns.keys()
    insert_data = {
        k: v for k, v in request_data.items() if k in all_column_names
    }
    insert_data['creator_id'] = token_auth.current_user().id
    insert_data['creation_timestamp'] = datetime.utcnow()
    insert_data['deleted'] = False
    insert_data_list = [(k, v) for k, v in insert_data.items()]

    insert_thread_query = f"""
    INSERT INTO thread 
    ({', '.join([k for k, v in insert_data_list])})
    VALUES ({', '.join([f"'{v}'" for k, v in insert_data_list])}) 
    RETURNING thread.id
    """
    query_result = database.session.execute(insert_thread_query)
    database.session.commit()
    new_thread_id = [r for r in query_result][0][0]
    response = jsonify({'thread_id': new_thread_id})
    response.status_code = 201
    response.headers['Location'] = url_for('get_thread', thread_id=new_thread_id)
    return response


@app.route('/api/v1/threads/<int:thread_id>', methods=['GET'])
@token_auth.login_required
def get_thread(thread_id):
    thread_query = SINGLE_THREAD_QUERY_TEMPLATE.format(thread_id)
    json_thread = get_single_json_entity(thread_query)
    if json_thread:
        response = jsonify(json_thread)
    else:
        response = error_response(404)
    return response


@app.route('/api/v1/threads/<int:thread_id>', methods=['DELETE'])
@token_auth.login_required
def remove_thread(thread_id):
    thread_query = SINGLE_THREAD_QUERY_TEMPLATE.format(thread_id)
    json_thread = get_single_json_entity(thread_query)
    if not json_thread:
        return error_response(404)
    if token_auth.current_user().id != json_thread['creator_id']:
        abort(403)

    delete_thread_query = f"""
    UPDATE thread SET deleted = TRUE WHERE thread.id = '{thread_id}';
    UPDATE post SET deleted = TRUE, deleted_by_thread = TRUE 
    WHERE post.thread_id = '{thread_id}'
    """
    database.session.execute(delete_thread_query)
    database.session.commit()
    response = jsonify({'status': 'OK'})
    return response


@app.route('/api/v1/threads/restore', methods=['POST'])
@token_auth.login_required
def restore_thread():
    app.logger.debug(f'Receive request: {request.data}')
    request_data = request.get_json() or {}
    if 'thread_id' not in request_data:
        return bad_request('must include a thread_id')

    thread_id = request_data['thread_id']
    deleted_thread_query = f"""
    SELECT
    thread.id, thread.name, thread.short_name, thread.creator_id,
    thread.creation_timestamp, thread.creator_id, thread.text, 
    thread.forum_id, thread.deleted
    FROM thread WHERE thread.id = '{thread_id}'
    """
    query_result_proxy = database.session.execute(deleted_thread_query)
    row_proxies = [r for r in query_result_proxy]
    if not row_proxies:
        return bad_request(f'can not restore the thread with id {thread_id}')

    json_thread = {k: v for k, v in row_proxies[0].items()}
    if token_auth.current_user().id != json_thread['creator_id']:
        abort(403)

    if not json_thread['deleted']:
        return bad_request(f'The thread with id {thread_id} is not deleted')

    restore_thread_query = f"""
    UPDATE thread SET deleted = FALSE WHERE thread.id = '{thread_id}';
    UPDATE post SET deleted = FALSE, deleted_by_thread = FALSE 
    WHERE post.thread_id = '{thread_id}' AND post.deleted_by_thread = TRUE
    """
    database.session.execute(restore_thread_query)
    database.session.commit()
    response = jsonify({'status': 'OK'})
    response.headers['Location'] = url_for('get_thread', thread_id=thread_id)
    response.status_code = 201
    return response

