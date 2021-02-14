import logging
import random

from faker import Faker
import requests


logger = logging.getLogger(__file__)


def test_create_post():
    fake = Faker()
    user_info = {
        'username': fake.first_name() + str(random.randint(1, 1000)),
        'common_name': fake.name(),
        'email': fake.email(),
        'password': 'pass'
    }
    logger.info(f'Create the user: {user_info}')
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/users/create',
        json=user_info
    )
    logger.info(f'Get response: {response.text}')

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Get response: {response.text}')
    token = response.json()['token']

    post_text = fake.text()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/create',
        json={'text': post_text},
        headers=headers
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    post_id = response_json.get('post_id')
    assert post_id
    assert isinstance(post_id, int)