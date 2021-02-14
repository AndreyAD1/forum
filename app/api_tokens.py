from flask import jsonify
from app import app, database
from app.api_auth import basic_auth


@app.route('/api/v1/tokens', methods=['POST'])
@basic_auth.login_required
def get_token():
    token = basic_auth.current_user().get_token()
    database.session.commit()
    return jsonify({'token': token})
