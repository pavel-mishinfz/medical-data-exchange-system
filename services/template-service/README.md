# API сервиса шаблонов


| Ресурс                   | Метод  | Что делает                    |
|--------------------------|--------|-------------------------------|
| /templates/{template_id} | GET    | Возвращает шаблон             |
| /templates               | GET    | Возвращает список всех шаблон |
| /templates               | POST   | Добавляет шаблон в базу       |
| /templates/{template_id} | PUT    | Обновляет шаблон              |
| /templates/{template_id} | DELETE | Удаляет шаблон из базы        | 


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
export POSTGRES_DSN=postgresql://psgadmin:1111@192.168.144.1:5432/medical-system 
export PATH_TO_STORAGE=/src/storage/ 
uvicorn app:app --reload
```

# Конфигурация
| Переменная      | Назначение                      | Значение по умолчанию                        |
|-----------------|---------------------------------|----------------------------------------------|
| POSTGRES_DSN    | Строка подключения к PostgreSQL | postgresql://user:pass@localhost:5432/foobar | 
| PATH_TO_STORAGE | Строка пути для хранения файлов | /src/storage/                                | 

# Документация

После запуска доступна документация: http://127.0.0.1:5000/docs

# Сборка образа
```bash
docker build -t medical-system/template-service:0.1 .
```

# Модули сервиса

- App - Точка входа в приложение, реализует FastAPI-приложение соответсвии с требованиями
- Schemas - Реализует Pydantic-схемы сущностей приложения
- Database - Реализует взаимодействией с базой данных - подключение к ней и sqalchemy-модели
- CRUD - Реализует CRUD-методы для работы с сущностями сервиса
- Config - Отвечает за подгрузку конфигурации


```mermaid
graph TD
    App --> CRUD
    App --> Database
    CRUD --> Database
    CRUD --> Schemas
    App --> Schemas
    App --> Config
```
