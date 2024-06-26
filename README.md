# Система обмена медицинскими данными

## Структура репозитория

- services - Директория содержит исходные коды сервисов системы
    - [chat-service](/services/chat-service) - сервис чатов и видеоконсультаций
    - [health-diary-service](/services/health-diary-service) - сервис дневника здоровья
    - [medical-card-service](/services/medical-card-service) - сервис медицинских карт
    - [policy-enforcement-service](/services/policy-enforcement-service) - сервис проверки полномочий
    - [record-service](/services/record-service) - сервис записей на прием
    - [template-service](/services/template-service) - сервис шаблонов страниц медкарты
    - [user-service](/services/user-service) - пользовательский сервис

## Концепция

Оперативный обмен информацией о состоянии здоровья, результатами обследований и рекомендациями между врачами и пациентами способствует оказанию качественной медицинской помощи. Благодаря данной системе пациенты получают легкий доступ к своим медицинским данным, что способствует их активному вовлечению в процесс лечения и управлению своим здоровьем.

### Основыне функции системы

- Ведение врачом электронной медицинской карты 
- Создание шаблонов для страниц медицинской карты 
- Просмотр медицинской карты пациентом 
- Онлайн запись на прием 
- Ведение пациентом "Дневника здоровья"
- Проведение онлайн-консультаций врачами 
- Взаимодействие врачей и пациентов в личных чатах

### Состав сервисов системы

- Сервис проверки полномочий (Policy Enforcement Service) - Является точкой входа в приложение, принимает все входящие запросы, проверяет права доступа к запрашиваемому ресурсу и маршрутизирует на него
- Пользовательский сервис (User Service) - Предоставляет API для регистрации и авторизации пользователей, для управления пользователями
- Сервис шаблонов (Template Service) - Предоставляет API для создания шаблонов страниц медкарты и работы с ними
- Сервис медицинских карт (Medical Card Service) - Предоставляет API для работы с медкартами и ее страницами
- Сервис дневников здоровья (Health Diary Service) - Предоставляет API для работы с записями в дневнике здоровья 
- Сервис записей на прием (Record Service) - Предоставляет API для работы с записями на прием, а также API для управления графиком работы врачей 
- Сервис взаимодействия (Chat Service) - Предоставляет API для взаимодействия пациентов и врачей в личных чатах, а также для проведения онлайн-консультаций

### Подсистема хранения данных
- PostgreSQL

### Полномочия системы:
- Администратор
- Врач
- Пациент

## Архитектура

![alt text](architecture.png "Architecture")

## [Развертывание](/deploy)

## [Посмотреть демо](https://medical-system.ru)