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
    assert response.status_code == 201
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

    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/create',
        json={'text': fake.text(), 'thread_id': thread_id},
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    post_id = response_json.get('post_id')
    assert post_id
    assert isinstance(post_id, int)


def test_get_post():
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
    assert response.status_code == 201
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

    post_text = fake.text()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/create',
        json={'text': post_text, 'thread_id': thread_id},
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    post_id = response.json().get('post_id')

    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/posts/{post_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 200
    expected_post = {
        'id': post_id,
        'text': post_text,
        'user_id': user_id
    }
    logger.info(f'Receive response: {response.text}')
    returned_post = response.json()
    returned_post.pop('creation_timestamp')
    assert returned_post == expected_post


def test_delete_post():
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
    assert response.status_code == 201
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

    post_text = fake.text()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/create',
        json={'text': post_text, 'thread_id': thread_id},
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    post_id = response.json().get('post_id')

    response = requests.delete(
        f'http://127.0.0.1:5000/api/v1/posts/{post_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 200

    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/posts/{post_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 404


def test_restore_post():
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
    assert response.status_code == 201
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

    post_text = fake.text()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/create',
        json={'text': post_text, 'thread_id': thread_id},
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    post_id = response.json().get('post_id')

    response = requests.delete(
        f'http://127.0.0.1:5000/api/v1/posts/{post_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')

    response = requests.post(
        'http://127.0.0.1:5000/api/v1/posts/restore',
        json={'post_id': post_id},
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 201

    response = requests.get(
        f'http://127.0.0.1:5000/api/v1/posts/{post_id}',
        headers=headers
    )
    logger.info(f'Receive response: {response.text}')
    assert response.status_code == 200
    expected_post = {
        'id': post_id,
        'text': post_text,
        'user_id': user_id
    }
    logger.info(f'Receive response: {response.text}')
    returned_post = response.json()
    returned_post.pop('creation_timestamp')
    assert returned_post == expected_post
