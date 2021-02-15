import logging
import random

from faker import Faker
import requests


logger = logging.getLogger(__file__)


def test_create_forum():
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

    forum_info = {
        'name': fake.company() + str(random.randint(1, 1000)),
        'short_name': fake.company_suffix() + str(random.randint(1, 1000))
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/forums/create',
        headers=headers,
        json=forum_info
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    forum_id = response_json.get('forum_id')
    assert forum_id
    assert isinstance(forum_id, int)


def test_get_forum():
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
    user_id = response.json()['user_id']

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Get response: {response.text}')
    token = response.json()['token']

    forum_info = {
        'name': fake.company() + str(random.randint(1, 1000)),
        'short_name': fake.company_suffix() + str(random.randint(1, 1000))
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/forums/create',
        headers=headers,
        json=forum_info
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 201
    forum_id = response.json()['forum_id']

    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/forums/{forum_id}',
        headers=headers
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 200
    expected_forum = {'id': forum_id, 'creator_id': user_id, **forum_info}
    assert response.json() == expected_forum
