# API сервиса управления пользователями

Реализован на основе фреймворка [fastapi-users](https://fastapi-users.github.io/)


# Что необходимо реализовать

- Подключить возможность авторизации через сторонние сервисы (например, Google)

# Зависимости

Перед запуском сервиса необходимо установить зависимости из файла requirements.txt

# Запуск

```bash
uvicorn app:app --port 5000 --reload
```

или

```bash
./run.sh
```

# Запуск с использование файла конфигурации .env

Для запуска из файла конфигурации нужно поместить файл .env в корень сервиса

# Конфигурация
| Переменная                  | Назначение                                                         | Значение по-умолчанию                        |
|-----------------------------|--------------------------------------------------------------------|----------------------------------------------|
| POSTGRES_DSN_ASYNC          | Строка подключения к PostgreSQL                                    | postgresql://user:pass@localhost:5432/foobar |
| JWT_SECRET                  | Парольная фраза, используемая для кодирования jwt-токена           | jwt_secret                                   | 
| RESET_PASSWORD_TOKEN_SECRET | Парольная фраза, используемая для кодирования токена сброса пароля | reset_password_token_secret                  | 
| VERIFICATION_TOKEN_SECRET   | Парольная фраза, используемая для кодирования токена верификации   | verification_token_secret                    |
| OWN_EMAIL                   | Email отправителя                                                  | user@example.com                             |
| OWN_EMAIL_PASSWORD          | Пароль для email отправителя                                       | password                                     |

# Документация

После запуска доступна документация: http://127.0.0.1:5000/docs

# Сборка образа
```bash
docker build -t medical-system/user-service:0.0.1 .
```