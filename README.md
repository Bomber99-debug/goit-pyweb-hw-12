# GoIT Python Web Homework 12

Простий вебзастосунок на стандартних модулях Python.

Застосунок запускає два сервери в окремих потоках:

* HTTP-сервер на порту `3000`;
* UDP Socket-сервер на порту `5000`.

## Функціональність

* сторінки `index.html` і `message.html`;
* обробка CSS-файлів та зображень;
* сторінка `error.html` для помилки `404 Not Found`;
* приймання даних із HTML-форми;
* передавання даних до Socket-сервера через UDP;
* збереження повідомлень у `storage/data.json`;
* запуск через Docker Compose.

## Схема роботи

```text
Браузер
   |
   | HTTP, порт 3000
   v
HTTP-сервер
   |
   | UDP, порт 5000
   v
Socket-сервер
   |
   v
storage/data.json
```

Ключем кожного повідомлення у JSON-файлі є дата і час його отримання.

## Локальний запуск

Встановити залежності:

```bash
poetry install --no-root
```

Запустити застосунок:

```bash
poetry run python main.py
```

Відкрити у браузері:

```text
http://localhost:3000
```

## Запуск через Docker Compose

Побудувати образ і запустити контейнер:

```bash
docker compose up --build
```

Запуск у фоновому режимі:

```bash
docker compose up --build -d
```

Зупинка контейнера:

```bash
docker compose down
```

## Збереження даних

У `docker-compose.yml` використовуються bind mounts:

```yaml
volumes:
  - ./storage:/app/storage
  - .:/app
```

Папка `storage` зберігається на комп’ютері, тому файл `storage/data.json` не видаляється разом із контейнером.

Перед запуском файл `storage/data.json` повинен існувати та містити валідний JSON:

```json
{}
```

## Порти

* `3000/TCP` — HTTP-сервер;
* `5000/UDP` — внутрішній Socket-сервер.
