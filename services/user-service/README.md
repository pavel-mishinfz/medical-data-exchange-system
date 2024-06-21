# API сервиса управления пользователями

Реализован на основе фреймворка [fastapi-users](https://fastapi-users.github.io/)

## Дополнительные маршруты

| Ресурс                                    | Метод  | Что делает                                            | Доступ               |
|-------------------------------------------|--------|-------------------------------------------------------|----------------------|
| /users/me/image                           | PATCH  | Обновляет изображение в профиле текущего пользователя | Пользователь         |
| /users/me/image                           | DELETE | Удаляет изображение в профиле текущего пользователя   | Пользователь         |
| /users/me/email                           | PATCH  | Обновляет почту текущего пользователя                 | Пользователь         |
| /users/{id}/image                         | PATCH  | Обновляет изображение в профиле пользователя          | Администратор        |
| /users/{id}/image                         | DELETE | Удаляет изображение в профиле пользователя            | Администратор        |
| /users/{user_id}/email                    | POST   | Обновляет почту пользователя                          | Администратор        |
| /users/user/{user_id}/summary             | GET    | Возвращает основную информацию о пользователе         | Пользователь         |
| /users/all/summary                        | GET    | Возвращает список всех пользователей                  | Администратор, Врач  |
| /users/specialization/{specialization_id} | GET    | Возвращает список врачей конкретной специализации     | Пользователь         |
| /specializations                          | POST   | Создает специализацию                                 | Администратор        |
| /specializations                          | GET    | Возвращает список специализаций                       | Пользователь         |
| /specializations/{specialization_id}      | GET    | Возвращает информацию о специализации                 | Пользователь         |
| /specializations/{specialization_id}      | PATCH  | Обновляет информацию о специализации                  | Администратор        |
| /specializations/{specialization_id}      | DELETE | Удаляет информацию о специализации                    | Администратор        |
| /send_confirm_code                        | POST   | Создает новый код подтверждения                       | Пользователь         |
| /check_confirm_code                       | POST   | Проверяет код подтверждения                           | Пользователь         |

# Зависимости

Перед запуском сервиса необходимо установить зависимости из файла requirements.txt

# Запуск

```bash
uvicorn app:app --port 5000 --reload
```

# Запуск с использование файла конфигурации .env

Для запуска из файла конфигурации нужно поместить файл .env в корень сервиса

# Конфигурация
| Переменная                          | Назначение                                                         | Значение по-умолчанию                         |
|-------------------------------------|--------------------------------------------------------------------|-----------------------------------------------|
| POSTGRES_DSN_ASYNC                  | Строка подключения к PostgreSQL                                    | postgresql://user:pass@localhost:5432/foobar  |
| JWT_SECRET                          | Парольная фраза, используемая для кодирования jwt-токена           | jwt_secret                                    | 
| RESET_PASSWORD_TOKEN_SECRET         | Парольная фраза, используемая для кодирования токена сброса пароля | reset_password_token_secret                   | 
| VERIFICATION_TOKEN_SECRET           | Парольная фраза, используемая для кодирования токена верификации   | verification_token_secret                     |
| OWN_EMAIL                           | Email отправителя                                                  | user@example.com                              |
| OWN_EMAIL_PASSWORD                  | Пароль для email отправителя                                       | password                                      |
| SMTP_SERVER                         | smtp-сервер                                                        | smtp.gmail.com                                |
| SMTP_PORT                           | Порт smtp-сервера                                                  | 465                                           |
| DEFAULT_GROUPS_CONFIG_PATH          | Путь к файлу с данными о группах                                   | default-groups.json                           |
| DEFAULT_SPECIALIZATIONS_CONFIG_PATH | Путь к файлу с данными о специализациях                            | default-specializations.json                  |
| PATH_TO_STORAGE                     | Путь к хранилищу пользовательских файлов                           | storage/                                      |
# Документация

После запуска доступна документация: http://127.0.0.1:5000/docs

# Сборка образа
```bash
docker build -t medical-system/user-service:0.0.1 .
```

или 

```bash
./build_image.sh
```