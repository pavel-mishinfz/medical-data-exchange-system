# Развертывание СУБД и сервисов

# Содержание
1. [Запуск](#запуск)
2. [Остановка](#остановка)
3. [MongoDB](#mongodb)
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

# MongoDB

За развертывание MongoDB отвечает следующая часть compose-файла:

```bash
volumes:
  mongo-data:
    driver: local
    driver_opts:
      o: bind
      type: none
      device: ./mongo/data
services:
  mongo:
    image: mongo:7.0
    volumes:
      - mongo-data:/data/db
      - ./mongo/init-mongo.js:/docker-entrypoint-initdb.d/init-mongo.js
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_DATABASE=medical-system
```

В нем:
- Создается диск (volume) с названием **mongo-data**, для хранения данных используется директория ./mongo/data. Рекомендуется добавить директорию в gitignore:

```bash
deploy/mongo/data/*
!deploy/mongo/data/.gitkeep
```
- Создается контейнер **mongo** на базе образа mongo:7.0
- К контейнеру монтируется volume **mongo**
- К контейнеру монтируется файл-конфигурации **init-mongo.js**
- Пробрасываются порты, Mongo будет доступна по {MACHINE_IP}:27017, например: 192.168.144.1:27017.
Для подключения можно использовать строку:
```bash
mongodb://mongoadmin:1111@192.168.144.1:27017/?authSource=medical-system
```
- Через переменную окружения дается название первичной базе данных:
```bash
MONGO_INITDB_DATABASE=medical-system
```

Также в развертывание используется файл **init-mongo.js**:
```bash
db.createUser(
    {
        user    : "mongoadmin",
        pwd     : "1111",
        roles   : [
            {
                role: "readWrite",
                db  : "medical-system"
            }
        ]    
    }
)
```

В нем создается пользователь с паролем и назначаются привелегии на запись в базу данных

Для тестирования подключения можно использовать MongoDB Atlas или любой другой GUI-клиент

## [Образ на Docker-хабе](https://hub.docker.com/_/mongo)
---

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
      POSTGRES_PASSWORD: 1111
      POSTGRES_USER: psgadmin
      POSTGRES_DB: medical-system
      PGDATA: /var/lib/postgresql/data/db-files/
    ports:
      - "5432:5432"
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
- Через переменные окружения задается пользователь, название первичной базы данных и директория хранения данных внутри контейнера:
```bash
POSTGRES_PASSWORD: 1111
POSTGRES_USER: psgadmin
POSTGRES_DB: medical-system
PGDATA: /var/lib/postgresql/data/db-files/
```

Для тестирования подключения можно использовать утилиту psql или какой-либо GUI-клиент

## [Образ на Docker-хабе](https://hub.docker.com/_/postgres)
---
