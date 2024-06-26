# API сервиса дневников здоровья

| Ресурс                   | Метод  | Что делает                                      | Доступ        |
|--------------------------|--------|-------------------------------------------------|---------------|
| /diaries/user/{user_id}  | POST   | Добавляет страницу дневника в базу              | Пациент       |
| /diaries/user/{user_id}  | GET    | Возвращает список страниц дневника пользователя | Врач, Пациент |
| /diaries/{page_diary_id} | PUT    | Обновляет страницу дневника                     | Пациент       |
| /diaries/{page_diary_id} | DELETE | Удаляет страницу дневника из базы               | Пациент       |      

# Зависимости

Перед запуском сервиса необходимо установить зависимости из файла requirements.txt

# Запуск

```bash
uvicorn app:app --port 5000 --reload
```

# Запуск с использование файла конфигурации .env

Для запуска из файла конфигурации нужно поместить файл .env в корень сервиса

# Запуск с переопределением переменных окружения

```bash
uvicorn app:app --port 5000 --reload
```

или

```bash
export POSTGRES_DSN_ASYNC=postgresql+asyncpg://postgres:postgres@localhost:5432/postgres 
uvicorn app:app --reload
```

# Конфигурация
| Переменная          | Назначение                       | Значение по умолчанию                                |
|---------------------|----------------------------------|------------------------------------------------------|
| POSTGRES_DSN_ASYNC  | Строка подключения к PostgreSQL  | postgresql+asyncpg://user:pass@localhost:5432/foobar |

# Документация

После запуска доступна документация: http://127.0.0.1:5000/docs

# Сборка образа
```bash
docker build -t medical-system/health-diary-service:0.0.1 .
```

или

```bash
./build_image.sh
```