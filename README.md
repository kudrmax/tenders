# Avito Tender Management API

Тестовое задание на позицию стажера по backend разработке в Авито.

Stack: `Python`, `FastAPI`, `SQLAlchemy`, `Pydantic`

## Задание

- [openapi](task/openapi.yml)
- [задание текстом](task/README_задание.md)

## Запуск

Создайте виртуальное окружение, активируйте его и установите необходимые зависимости:
```shell
git clone https://github.com/kudrmax/tenders
cd tenders
python3 -m venv venv
source venv/bit/activate  # для unix
.\venv\Scripts\activate.bat  # для windows
pip3 install -r requirements.txt
```

Чтобы создать таблицы в базе данных (если их нет) запустите:
```shell
python3 src/database/init_db.py
```

Установите переменные окружения (например в файл `.env`)
```
SERVER_ADDRESS=0.0.0.0:8080
POSTGRES_USERNAME=...
POSTGRES_PASSWORD=...
POSTGRES_HOST=...
POSTGRES_PORT=
POSTGRES_DATABASE=...
```

Запустить сервис:
```shell
python3 main.py
```

Swagger находится по [cсылке](https://cnrprod1725726225-team-77183-32753.avito2024.codenrock.com) или в случае
самостоятельно поднятого сервера по пути `/` или `/docs`.


## Устройство проекта

### База данных

![](/docs/er.png)

### Swagger

![](/docs/openapi.png)
