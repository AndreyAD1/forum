# Forum API
Сервис, имитирующий API интернет-форума. Проект написан на Python 3.9, 
основной фреймворк - Flask, база данных - PostgreSQL 13.

## Запуск
Перед запуском сервиса необходимо установить [docker-compose](https://docs.docker.com/compose/) и
назначить следующие переменные окружения:
```shell
# логин роли Postgres, от имени которой будут выполняться операции с БД
FORUM_DB_USER
# пароль роли Postgres, от имени которой будут выполняться операции с БД
FORUM_DB_PASSWORD
# путь, где будет храниться БД сервиса на хосте
FORUM_DB_PATH
# путь, где будет храниться БД сервиса в контейнере Postgres
PGDATA
# пароль суперюзера Postgres
POSTGRES_PASSWORD
```
Запуск выполняется командой:
```shell
docker-compose up --build -d
```
После запуска поднимутся два контейнера: `forum_db` - сервер БД PostgreSQL и
`forum` - сервис API.
Сервис будет ожидать запросы по адресу `http://0.0.0.0:8000/api/v1`.

## Описание API
### Создание пользователя 
Метод: `POST`

Путь: `api/v1/users/create`

Аутентификация: нет

В теле запроса ожидается JSON с ключами `username`, `common_name` `email`, `password`.
В случае успешной обработки запроса от сервера придет ответ вида `{"user_id": "some_id"}`.

### Получение токена
Метод: `POST`

Путь: `api/v1/tokens`

Аутентификация: basic access authentication. В заголовке запроса нужно указать 
`username` и пароль созданного пользователя.

В случае успешной обработки запроса от сервера придет ответ вида `{"token": "user_token"}`.

**Для всех методов, перечисленных ниже, используется аутентификация
bearer authentication. В заголовке запроса нужно указать действующий токен.**

### Создание форума
Метод: `POST`
   
Путь: `api/v1/forums/create`

В теле запроса ожидается JSON с ключами `name` и `short_name`.
В случае успешной обработки запроса от сервера придет ответ вида `{"forum_id": "some_id"}`.

### Создание треда сообщений
Метод: `POST`

Путь: `api/v1/threads/create`

В теле запроса ожидается JSON с ключем `forum_id`. Опционально можно указать ключи
`name`, `short_name`, `text`.
В случае успешной обработки запроса от сервера придет ответ вида `{"thread_id": "some_id"}`.

### Создание сообщения
Метод: `POST`

Путь: `api/v1/posts/create`

В теле запроса ожидается JSON с ключем `text` и `thread_id`.
В случае успешной обработки запроса от сервера придет ответ вида `{"post_id": "some_id"}`.

### Получение подробной информации о сущности
Метод: `GET`

Путь:`api/v1/<название сущности>/<id сущности>`. Например, `api/v1/users/5`

В теле ответа сервера придет JSON со всеми доступными свойствами сущности.

### Обновление информации о пользователе 
Метод: `PUT`

Путь: `api/v1/users/<id пользователя>`

В теле запроса ожидается JSON с ключами доступных для изменения свойств
пользователя: `username`, `email`, `common_name`.

### Получение всех сообщений пользователя и всех тредов форума
Метод: `GET`

Путь для получения сообщений: `/api/v1/users/<user_id>/posts`
Путь для получения тредов: `/api/v1/forums/<forum_id>/threads`

В теле ответа сервера придет JSON с информацией о всех постах пользователя и
тредах форума соответственно.

### Удаление тредов и сообщений
Метод: `DELETE`

Путь для удаления сообщений: `/api/v1/posts/<post_id>`
Путь для удаления тредов: `/api/v1/threads/<thread_id>`

При удалении треда будут удалены все сообщения, которые он содержит.

### Восстановление тредов и сообщений
Метод: `POST`

Путь для восстановления сообщений: `/api/v1/posts/restore`
Путь для восстановления тредов: `/api/v1/threads/restore`

При восстановлении треда будут восстановлены сообщения, удаленные из-за удаления треда.

## Запуск тестов

Тесты расположены в директории [tests](/tests). Для их запуска потребуется поднять сервис
вне докер-контейнеров.

Предварительно необходимо установить Python 3.9 и Postgres 13.2.

1. Установка зависимостей Python;
```shell
pip install -r requirements-dev.txt
```
2. Создание в Postgres базы данных, которую будет использовать сервис. 
Скрипт инициализации БД находится [здесь](/db_config/initialize_db.sh).
   
3. Назначить переменные окружения
```shell
export FLASK_APP=forum.py
export DATABASE_URL=postgresql://<db_user>:<db_password>@localhost/<db_name>
```

4. Провести миграции БД и запустить сервис.
```shell
flask db upgrade
flask run
```

5. Запустить тесты. Тесты ожидают, что сервис слушает запросы по адресу `http://127.0.0.1:5000/`.
```shell
pytest ./tests/
```
