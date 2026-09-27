# Aiohttp API

Асинхронный REST API для работы с объявлениями.

Проект выполнен на `aiohttp` с использованием асинхронного SQLAlchemy и PostgreSQL. Реализована JWT-аутентификация пользователей и проверка прав владельца объявления.

## Стек

- Python 3.12
- aiohttp
- SQLAlchemy 2.0 Async
- asyncpg
- PostgreSQL 16
- PyJWT
- Passlib
- bcrypt
- Docker Compose

## Возможности

### Пользователи

- регистрация;
- авторизация;
- получение JWT-токена;
- проверка пароля;
- защита API с помощью Bearer Token.

### Объявления

- создание объявления;
- получение списка объявлений;
- получение объявления по ID;
- изменение объявления;
- удаление объявления;
- проверка владельца при изменении и удалении.

## Структура проекта

```text
aiohttp_ads/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── db.py
│   ├── handlers.py
│   ├── init_db.py
│   ├── main.py
│   └── models.py
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Запуск проекта

### 1. Клонирование репозитория

```bash
git clone git@github.com:skursina/aiohttp_ads.git
cd aiohttp_ads
```

### 2. Создание виртуального окружения

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Запуск PostgreSQL

```bash
docker compose up -d
```

PostgreSQL доступен на:
```
localhost:5433
```

Порт `5433` используется потому, что стандартный порт `5432` занят локальным PostgreSQL.

### 5. Создание таблиц

```bash
python -m app.init_db
```

### 6. Запуск API

```bash
python -m app.main
```

API будет доступно по адресу:

```bash
http://localhost:8000
```

## API
### Проверка API
```http
GET /
```
Пример ответа:

```json
{
  "message": "Aiohttp API работает"
}
```

### Регистрация
```http
POST /auth/register
```
Пример:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

### Авторизация
```http
POST /auth/login
```

Пример:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

Ответ содержит JWT:
```json
{
  "access_token": "YOUR_TOKEN",
  "token_type": "Bearer"
}
```

Полученный токен используется для защищённых запросов:
```
Authorization: Bearer YOUR_TOKEN
```

## Работа с объявлениями
### Создание объявления

```http
POST /ads
```

Требуется авторизация.
```bash
curl -X POST http://localhost:8000/ads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Новое объявление","description":"Описание объявления"}'
```

### Получение всех объявлений

```http
GET /ads
```
```bash
curl http://localhost:8000/ads
```

### Получение объявления
```http
GET /ads/{ad_id}
```
```bash
curl http://localhost:8000/ads/1
```

### Изменение объявления
```http
PATCH /ads/{ad_id}
```

Требуется авторизация владельца объявления.
```bash
curl -X PATCH http://localhost:8000/ads/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Изменённое объявление"}'
```

### Удаление объявления

```http
DELETE /ads/{ad_id}
```

Требуется авторизация владельца объявления.
```bash
curl -X DELETE http://localhost:8000/ads/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## HTTP-коды

|Код	| Значение|
|-------|---------|
|200	|Успешный запрос|
|201	|Ресурс создан|
|204	|Ресурс успешно удалён|
|400	|Некорректные данные|
|401	|Требуется авторизация|
|403	|Недостаточно прав|
|404	|Ресурс не найден|
|409	|Пользователь уже существует|

## Аутентификация

Для защищённых endpoints используется JWT.

После авторизации клиент получает токен:
```
access_token
```

Токен передаётся в HTTP-заголовке:
```
Authorization: Bearer <token>
```
При изменении или удалении объявления дополнительно проверяется, является ли текущий пользователь его владельцем.