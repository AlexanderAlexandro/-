# Mini Messenger MVP

Основа простого браузерного мини-мессенджера без лишней инфраструктуры. Проект собран на стандартной библиотеке Python и нативном фронтенде, чтобы MVP можно было быстро поднять и дальше спокойно развивать.

## Стек

- Backend: Python 3 `http.server` + SQLite-backed store
- Realtime: Server-Sent Events
- Frontend: HTML + CSS + vanilla JavaScript ES modules
- Data storage: SQLite
- Config: `.env` без внешних зависимостей

## Почему такой стек

- Репозиторий начинался с очень простого статического прототипа, поэтому для MVP важнее был быстрый и прозрачный старт, чем инфраструктура ради инфраструктуры.
- Стек не требует сборщика, базы данных или пакетов, а значит проект можно запускать сразу в development и постепенно усложнять.
- Текущую основу легко заменить на полноценный API, постоянное хранилище и WebSocket, когда появится необходимость.

## Что уже есть

- браузерный интерфейс с auth-экраном
- логин и регистрация
- выход из сессии
- приватный путь `/app` с редиректом для неавторизованных пользователей
- SQLite-хранилище с воспроизводимой схемой и seed
- список direct-чатов
- окно переписки
- отправка текстовых сообщений
- realtime обновление сообщений
- базовый online status
- адаптивный чистый UI

## Что пока специально упрощено

- сессии и online status по-прежнему завязаны на память процесса, хотя `last seen` сохраняется в SQLite
- нет production-ready ролей, восстановления пароля и полной security hardening-схемы
- нет вложений, уведомлений, поиска, групповых чатов и доставки/прочтения

## Структура

```text
backend/
  auth.py
  config.py
  database.py
  server.py
  store.py
  sql/schema.sql
frontend/
  index.html
  app.js
  styles.css
main.py
.env.example
README.md
Dockerfile
compose.yaml
deploy/Caddyfile
.env.production.example
```

## Запуск

1. Убедитесь, что установлен Python 3.
2. При необходимости скопируйте `.env.example` в `.env` и измените порт, host или путь к SQLite-файлу.
   Для локального MVP также можно ограничить максимальный размер JSON-запроса через `APP_REQUEST_BODY_LIMIT_BYTES`.
3. Создайте схему БД:

```bash
python3 main.py init-db
```

4. Загрузите тестовый seed:

```bash
python3 main.py seed-db
```

5. Запустите сервер:

```bash
python3 main.py
```

6. Откройте в браузере:

```text
http://127.0.0.1:8000
```

После входа приватная часть приложения живет на:

```text
http://127.0.0.1:8000/app
```

## Демо-аккаунты

- `alice` / `Password123!`
- `marco` / `Password123!`

## Схема БД

Простыми словами:

- `users`: учетные записи пользователей с логином, отображаемым именем и безопасно сохраненным паролем
- `chats`: сами чаты; сейчас используются direct-чаты, но поле `type` позволяет позже добавить групповые
- `chat_members`: связь многие-ко-многим между чатами и пользователями; для direct-чата здесь просто две строки
- `messages`: текстовые сообщения с автором, чатом и временными метками

Ключевые идеи схемы:

- direct-чаты ищутся по `direct_pair_key`, чтобы не создавать дубликаты между одной и той же парой пользователей
- групповые чаты можно добавить позже в ту же таблицу `chats`, используя `type='group'` и список участников в `chat_members`
- все основные сущности содержат timestamps
- связи и каскадное удаление обеспечиваются foreign keys SQLite

## Auth-проверка

Минимальный ручной сценарий:

1. Откройте `http://127.0.0.1:8000`.
2. Зарегистрируйте нового пользователя.
3. Убедитесь, что после регистрации открывается приватная часть `/app`.
4. Нажмите `Выйти` и проверьте, что приватная часть снова недоступна без входа.
5. Выполните вход под созданным пользователем или под demo-аккаунтом.

## Работа с базой

- Инициализация схемы: `python3 main.py init-db`
- Загрузка seed: `python3 main.py seed-db`
- По умолчанию база создается в `data/messenger.sqlite3`

## Публичный запуск для друзей

Если друзья будут заходить с разных сетей, самый простой и безопасный путь для этого MVP такой:

- один VPS
- домен или поддомен, который указывает на VPS
- Docker Compose
- HTTPS через Caddy

Что я добавил в репозиторий:

- [Dockerfile](/Users/a.vostretsov/Downloads/messanger/Dockerfile) для контейнера приложения
- [compose.yaml](/Users/a.vostretsov/Downloads/messanger/compose.yaml) для запуска app + Caddy
- [deploy/Caddyfile](/Users/a.vostretsov/Downloads/messanger/deploy/Caddyfile) для автоматического HTTPS
- [.env.production.example](/Users/a.vostretsov/Downloads/messanger/.env.production.example) как шаблон production-настроек

Как поднять публичную версию:

1. Возьмите VPS с публичным IP.
2. Откройте на сервере порты `80` и `443`.
3. Настройте DNS:
   `chat.example.com -> IP вашего VPS`
4. Скопируйте проект на сервер.
5. Создайте production env:

```bash
cp .env.production.example .env.production
```

6. Заполните в `.env.production`:

```text
APP_DOMAIN=chat.example.com
ACME_EMAIL=you@example.com
```

7. Запустите контейнеры:

```bash
docker compose --env-file .env.production up -d --build
```

8. Откройте в браузере:

```text
https://chat.example.com
```

Если хотите загрузить demo-данные и тестовые аккаунты на сервере:

```bash
docker compose --env-file .env.production exec app python3 main.py seed-db
```

Если demo-аккаунты не нужны, просто не запускайте `seed-db`, и пользователи смогут регистрироваться сами.

Важно для этого MVP:

- публичный запуск сейчас рассчитан на один сервер
- SQLite хранится в docker volume `messenger_data`
- после перезапуска контейнера база сохранится, но активные сессии и online presence пересоберутся заново

## Ближайшие шаги после MVP-основы

- при необходимости заменить SQLite на PostgreSQL
- вынести auth в отдельный сервисный слой
- перейти с SSE на WebSocket при усложнении realtime-сценариев
- добавить создание новых диалогов и историю сообщений из БД
