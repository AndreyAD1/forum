import requests


def test_create_user():
    user_info = {
        'username': 'test_user_3',
        'email': 'test_user_3@email.ru',
        'password': 'test_password_3'
    }
    response = requests.post(
        'http://127.0.0.1:5000/api/v1/users/create',
        json=user_info
    )
    print(response.text)
    assert response.status_code == 201
    response_json = response.json()
    assert len(response_json) == 1
    user_id = response_json.get('user_id')
    assert user_id
    assert isinstance(user_id, int)
