# Avito Tender Management API

Тестовое задание на позицию стажера по backend разработке в Авито.

## Задание

- [openapi](task/openapi.yml)
- [задание текстом](task/README_задание.md)

## Запуск

Для локального запуска создайте виртуально окружение, установите пакеты из `requirements.txt` и запустите
файл `main.py`.

Чтобы создать таблицы в базе данных (если их нет) запустите `src/database/init_db.py`.

Swagger находится по [cсылке](https://cnrprod1725726225-team-77183-32753.avito2024.codenrock.com) или в случае
самостоятельно поднятого сервера по пути `/` или /docs

Переменные окружения, необходимые для работы:

```
SERVER_ADDRESS=0.0.0.0:8080
POSTGRES_USERNAME=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=...
POSTGRES_PORT=
POSTGRES_DATABASE=...
```

## Устройство проекта

### База данных

![](/docs/er.png)

### Swagger

![](/docs/openapi.png)