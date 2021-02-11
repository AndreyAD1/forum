from flask import request, jsonify

from app import app, database
from app.models import User


@app.route('/api/v1/users/create', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    user = User()
    user.from_dict(data, new_user=True)
    database.session.add(user)
    database.session.commit()
    response = jsonify({})
    response.status_code = 201
    return response
