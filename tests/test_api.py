import logging

from faker import Faker
import requests


logger = logging.getLogger(__file__)


def test_create_user():
    fake = Faker()
    user_info = {
        'username': fake.name(),
        'email': fake.email(),
        'password': 'pass'
    }
    logger.info(f'Create the user: {user_info}')
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/users/create',
        json=user_info
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    user_id = response_json.get('user_id')
    assert user_id
    assert isinstance(user_id, int)
