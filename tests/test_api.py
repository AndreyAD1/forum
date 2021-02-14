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


def test_get_token():
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

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Get response: {response.text}')
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 1
    token = response_json.get('token')
    assert token


def test_get_user():
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
    user_id = response.json()['user_id']

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Get response: {response.text}')
    token = response.json()['token']

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/users/{user_id}',
        headers=headers
    )
    logger.info(f'Get response: {response.text}')
    expected_user = {
        'id': user_id,
        'username': user_info['username'],
        'email': user_info['email']
    }
    assert response.status_code == 200
    assert response.json() == expected_user


def test_update_user():
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
    user_id = response.json()['user_id']

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Get response: {response.text}')
    token = response.json()['token']

    headers = {'Authorization': f'Bearer {token}'}
    fields_to_update = {
        'username': fake.name(),
        'email': fake.email(),
    }
    response = requests.put(
        f'http://127.0.0.1:5000/api/v1/users/{user_id}',
        headers=headers,
        json=fields_to_update
    )
    logger.info(f'Get response: {response.text}')
    expected_user = {
        'id': user_id,
        'username': fields_to_update['username'],
        'email': fields_to_update['email']
    }
    assert response.status_code == 200
    assert response.json() == expected_user
