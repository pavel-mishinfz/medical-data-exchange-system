# Развертывание СУБД и сервисов

# Содержание
1. [Запуск](#запуск)
2. [Остановка](#остановка)
4. [PostgreSQL](#postgresql)

# Запуск
```bash
docker-compose -p medical-system up -d
```
## Проверка статусов сервисов

```bash
docker ps --all --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

# Остановка

```bash
docker-compose stop
```

# PostgreSQL

За развертывание PostgreSQL отвечает следующая часть compose-файла:

```bash
volumes:
  postgresql-data:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: ./postgresql/data
services:
  postgresql:
    image: postgres:14.9-alpine3.18
    volumes:
      - postgresql-data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: postgres
      PGDATA: /var/lib/postgresql/data/db-files/
    ports:
      - "5432:5432"
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}" ]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
```

В нем:

- Создается диск (volume) с названием **postgresql-data**, для хранения данных используется директория ./postgresql/data. Рекомендуется добавить директорию в gitignore:

```bash
deploy/postgresql/data/*
!deploy/postgresql/data/.gitkeep
```
- Создается контейнер **postgresql** на базе образа postgres:14.9-alpine3.18
- К контейнеру монтируется volume **postgresql-data**
- Пробрасываются порты, PostreSQL будет доступен по {MACHINE_IP}:5432, например: 192.168.144.1:5432.
- Через переменные окружения задается пользователь, пароль, название первичной базы данных и директория хранения данных внутри контейнера:
```bash
POSTGRES_PASSWORD: postgres
POSTGRES_USER: postgres
POSTGRES_DB: postgres
PGDATA: /var/lib/postgresql/data/db-files/
```

Для тестирования подключения можно использовать утилиту psql или какой-либо GUI-клиент

## [Образ на Docker-хабе](https://hub.docker.com/_/postgres)
---
