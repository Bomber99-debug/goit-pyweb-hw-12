# GoIT Python Web Homework 12

Найпростіший вебзастосунок, створений за допомогою стандартних модулів Python.

Застосунок містить HTTP-сервер для обробки вебсторінок і UDP Socket-сервер для приймання та збереження повідомлень із форми.

## Функціональність

* відображення головної сторінки `index.html`;
* відображення сторінки з формою `message.html`;
* обробка статичних ресурсів:

  * CSS-файлів;
  * зображень;
* повернення сторінки `error.html` зі статусом `404 Not Found`;
* приймання даних із HTML-форми;
* передавання даних від HTTP-сервера до Socket-сервера через UDP;
* збереження повідомлень у файл `storage/data.json`;
* запуск HTTP- і Socket-серверів у різних потоках;
* запуск застосунку через Docker Compose;
* збереження `data.json` поза файловою системою контейнера за допомогою bind mount.

## Схема роботи

```text
Браузер
   |
   | HTTP-запит
   v
HTTP-сервер: 0.0.0.0:3000
   |
   | UDP-повідомлення
   v
Socket-сервер: 127.0.0.1:5000
   |
   v
storage/data.json
```

Після надсилання форми HTTP-сервер отримує дані та передає їх Socket-серверу через UDP.

Socket-сервер перетворює отриманий байт-рядок у словник і записує його у файл `storage/data.json`.

Ключем кожного повідомлення є дата і час його отримання.

## Формат даних

```json
{
    "2026-07-22 22:30:31.974565": {
        "username": "User",
        "message": "Hello"
    },
    "2026-07-22 22:31:53.112066": {
        "username": "Admin",
        "message": "Second message"
    }
}
```

## Структура проєкту

```text
goit-pyweb-hw-12/
├── main.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── templates/
│   ├── index.html
│   ├── message.html
│   └── error.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── img/
│       └── logo.png
└── storage/
    └── data.json
```

## Використані технології

* Python 3.10 або новіший;
* `http.server`;
* UDP sockets;
* threading;
* Poetry;
* Docker;
* Docker Compose.

## Локальний запуск

### 1. Клонувати репозиторій

```bash
git clone https://github.com/Bomber99-debug/goit-pyweb-hw-12.git
cd goit-pyweb-hw-12
```

### 2. Встановити залежності

```bash
poetry install
```

### 3. Запустити застосунок

```bash
poetry run python main.py
```

Після запуску застосунок буде доступний за адресою:

```text
http://localhost:3000
```

## Маршрути

| Метод  | Маршрут                     | Опис                     |
| ------ | --------------------------- | ------------------------ |
| `GET`  | `/`                         | Головна сторінка         |
| `GET`  | `/message`                  | Сторінка з формою        |
| `POST` | `/message`                  | Надсилання даних форми   |
| `GET`  | `/static/...`               | Статичні ресурси         |
| `GET`  | будь-який невідомий маршрут | Сторінка `404 Not Found` |

## Запуск через Docker Compose

Для запуску застосунку необхідно мати встановлені Docker і Docker Compose.

### Побудова образу та запуск контейнера

```bash
docker compose up --build
```

Після запуску відкрити:

```text
http://localhost:3000
```

Для запуску контейнера у фоновому режимі:

```bash
docker compose up --build -d
```

## Перегляд логів

```bash
docker compose logs -f
```

## Зупинка контейнера

```bash
docker compose down
```

## Збереження даних

У `docker-compose.yml` використовується bind mount:

```yaml
volumes:
  - ./storage:/app/storage
```

Локальна папка:

```text
./storage
```

підключається до папки контейнера:

```text
/app/storage
```

Тому під час запису в контейнері до файла:

```text
/app/storage/data.json
```

дані фактично зберігаються у локальному файлі:

```text
storage/data.json
```

Після зупинки або видалення контейнера повідомлення не зникають.

## Перевірка збереження даних

1. Запустити застосунок:

```bash
docker compose up --build
```

2. Відкрити сторінку:

```text
http://localhost:3000/message
```

3. Надіслати повідомлення через форму.

4. Перевірити файл:

```text
storage/data.json
```

5. Зупинити та видалити контейнер:

```bash
docker compose down
```

6. Переконатися, що файл `storage/data.json` та записані повідомлення залишилися на комп’ютері.

## Порти

* `3000/TCP` — HTTP-сервер;
* `5000/UDP` — внутрішній Socket-сервер.

UDP-порт `5000` не публікується назовні, оскільки HTTP- і Socket-сервери працюють усередині одного контейнера.
