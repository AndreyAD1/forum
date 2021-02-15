import logging
import random

from faker import Faker
import requests


logger = logging.getLogger(__file__)


def test_create_thread():
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
    logger.info(f'Receive response: {response.text}')

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Receive response: {response.text}')
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
    logger.info(f'Receive response: {response.text}')
    forum_id = response.json()['forum_id']

    thread_info = {
        'name': fake.company() + str(random.randint(1, 1000)),
        'short_name': fake.company_suffix() + str(random.randint(1, 1000)),
        'text': fake.text(),
        'forum_id': forum_id
    }
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/threads/create',
        json=thread_info,
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    thread_id = response_json.get('thread_id')
    assert thread_id
    assert isinstance(thread_id, int)


def test_get_thread():
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
    logger.info(f'Receive response: {response.text}')
    user_id = response.json()['user_id']

    response = requests.post(
        f'http://127.0.0.1:5000/api/v1/tokens',
        auth=(user_info['username'], user_info['password'])
    )
    logger.info(f'Receive response: {response.text}')
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
    logger.info(f'Receive response: {response.text}')
    forum_id = response.json()['forum_id']

    thread_info = {
        'name': fake.company() + str(random.randint(1, 1000)),
        'short_name': fake.company_suffix() + str(random.randint(1, 1000)),
        'text': fake.text(),
        'forum_id': forum_id
    }
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/threads/create',
        json=thread_info,
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    thread_id = response.json()['thread_id']

    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/threads/{thread_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 200
    expected_post = {'id': thread_id, 'creator_id': user_id, **thread_info}
    logger.info(f'Receive response: {response.text}')
    returned_post = response.json()
    returned_post.pop('creation_timestamp')
    assert returned_post == expected_post
