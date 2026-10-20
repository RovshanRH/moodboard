# Mood board creator

Веб-бэкенд конструктора мудбордов для дизайнеров, фрилансеров и творческих
команд. Проект реализован на Django и использует SQLite для локальной разработки.
В ПР7 добавлен отдельный слой работы с SQLite через стандартный модуль `sqlite3`
и SQL-запросы.

## Предметная область

Основные сущности системы:

- `Designer` - профиль дизайнера, связанный со стандартным пользователем Django;
- `Moodboard` - мудборд с названием, описанием, цветом фона и палитрой из нескольких цветов;
- `MoodboardCatalog` - каталог мудбордов конкретного дизайнера;
- `Client` - заказчик, для которого создаётся мудборд.

`Moodboard` хранит связи с `Designer`, `MoodboardCatalog` и `Client`. Каталог
можно выбрать только среди каталогов текущего дизайнера, поэтому объекты
взаимодействуют через явные связи моделей, а не через разрозненные словари.

## Объектная модель

Основные сущности представлены классами Django-моделей:

- `Designer`: атрибуты `user`, `display_name`, `bio`; методы `owns_catalog()` и
	`owns_moodboard()`;
- `Client`: атрибуты `name`, `email`, `company`; метод `contact_label()`;
- `MoodboardCatalog`: атрибуты `designer`, `name`, `description`; метод
	`belongs_to()`;
- `Moodboard`: атрибуты `designer`, `catalog`, `client`, `title`, `description`,
	`background_color`, `created_at`, `updated_at`; методы `can_use_catalog()`,
	`assign_catalog()`, `assign_client()`, `change_background()` и `to_data()`.

Каждый класс имеет конструктор `__init__` и строковое представление `__str__`.
Коллекции объектов формируются Django QuerySet при работе с базой данных и
передаются в функции `storage.py`. Операции, относящиеся к одному объекту,
находятся в его методах, а поиск по коллекциям выполняется обычными функциями
`find_client()` и `find_catalog()`.

## Основные функции

### Авторизация

Регистрация создаёт пользователя Django, профиль выбранной роли и сессию.
По умолчанию роль — дизайнер, для заказчика передаётся `role: "client"`:

```http
POST /api/auth/
Content-Type: application/json

{
	"username": "anna",
	"password": "strong-password",
	"display_name": "Анна Дизайнер",
	"role": "designer"
}
```

Для регистрации заказчика нужны также `email` и роль:

```json
{
	"username": "client",
	"password": "strong-password",
	"display_name": "Студия Альфа",
	"email": "alpha@example.com",
	"role": "client"
}
```

Выход выполняется запросом `DELETE /api/auth/`.
В веб-интерфейсе выход выполняется кнопкой «Выйти» через
`POST /logout/` с CSRF-защитой.

## Веб-страницы

Веб-интерфейс доступен без API-префикса и использует Django-шаблоны,
Bootstrap 5.3 и статические файлы приложения:

- `templates/base.html` — общий базовый шаблон с блоками `title` и `content`;
- `templates/includes/navigation.html` — подключаемая навигация;
- `moodboards/templates/moodboards/includes/moodboard_card.html` —
  переиспользуемая карточка мудборда;
- `moodboards/static/moodboards/site.css` — собственные CSS-стили;
- `moodboards/static/moodboards/logo.svg` — логотип;
- `moodboards/static/moodboards/site.js` — JavaScript для интерактивного
  эффекта карточек.

- `GET /` — главная страница проекта;
- `GET /moodboards/` — список мудбордов;
- `GET/POST /moodboards/create/` — форма создания мудборда для дизайнера;
- `GET /moodboards/<id>/` — подробности мудборда (динамический URL);
- `GET /catalogs/` — список каталогов;
- `GET /clients/` — список заказчиков;
- `GET /search/?q=бренд` — параметризованный поиск мудбордов по названию;
- `GET /statistics/` — агрегированная статистика по данным SQLite;
- страницы мудбордов, каталогов и заказчиков связаны общими вкладками;
- неизвестные адреса обрабатываются страницей 404.

Шаблоны используют наследование через `{% extends %}`, блоки `{% block %}`,
включение через `{% include %}`, циклы, условия, фильтры
`default` и `truncatewords`, а ссылки формируются именованными URL
с пространством имён `moodboards`.

JSON API сохранён отдельно под префиксом `/api/`: `POST /api/auth/`,
`GET/POST /api/moodboards/`, `GET/POST /api/catalogs/` и
`GET /api/moodboards/<id>/export/`. Только дизайнер может создавать мудборды
и каталоги. При создании каталога поле `moodboard_ids` привязывает к нему
мудборды текущего дизайнера.

### Создание и просмотр мудбордов

Авторизованный дизайнер может получить собственные мудборды:

```http
GET /api/moodboards/
```

Создание мудборда:

```http
POST /api/moodboards/
Content-Type: application/json

{
	"title": "Новый бренд",
	"description": "Референсы для айдентики",
	"background_color": "#112233",
	"palette": ["#112233", "#AABBCC", "#DDEEFF"],
	"catalog_id": 1,
	"client_id": 1
}
```

`catalog_id` и `client_id` являются необязательными. Поле `palette` принимает список hex-цветов в формате `#RRGGBB`.
управляются через Django Admin: `/admin/`.

### Экспорт в PNG

Созданный мудборд экспортируется владельцем в PNG:

```http
GET /api/moodboards/<id>/export/
```

Файл формируется через Pillow и содержит название, описание и цвет фона мудборда.

## Структура проекта

Приложение разделено по ответственности:

- `accounts/` — регистрация, вход и профили дизайнера/заказчика;
- `boards/` — модели, страницы, API, экспорт и импорт мудбордов;
- `catalogs/` — модель, API каталогов, каталоги и список заказчиков;
- `moodboards/` — общая главная/404, совместимый слой миграций и старых URL.

Views распределены так же, как модели: account views обслуживают вход и
регистрацию, board views — CRUD/API/поиск/статистику мудбордов, catalog views —
каталоги и заказчиков. Старые `moodboards/urls.py` и `api_urls.py` сохраняют
совместимые точки входа, но импортируют обработчики из новых приложений.

Модели перенесены в новые приложения с сохранением имён существующих таблиц
`moodboards_*`. Миграции новых приложений используют
`SeparateDatabaseAndState`: схема базы не пересоздаётся, но Django теперь
владеет моделями через `accounts`, `boards` и `catalogs`. Legacy-модели
удалены только из состояния миграций, а совместимые реэкспорты позволяют
постепенно обновлять внешние импорты.

```text
moodboard/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── base.html
│   └── includes/
│       └── navigation.html
├── db/
│   ├── database.py
│   └── import_json.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── moodboards/
│   ├── api_urls.py
│   ├── templates/
│   ├── static/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       ├── export_data.py
│   │       └── import_data.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── catalog.py
│   │   ├── client.py
│   │   ├── designer.py
│   │   └── moodboard.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py
│   ├── storage.py
│   ├── admin.py
│   ├── apps.py
│   ├── urls.py
│   └── views.py
├── accounts/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── boards/
│   ├── migrations/
│   ├── models.py
│   ├── storage.py
│   ├── urls.py
│   └── views.py
├── catalogs/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── main.py
├── data/
│   ├── moodboards.json
│   └── roomly.sqlite
├── manage.py
└── requirements.txt
```

## Запуск

Установить зависимости:

```text
python -m pip install -r requirements.txt
```

Создать базу и запустить сервер:

```text
python manage.py migrate
python manage.py runserver
```

Создать структуру отдельной SQLite-базы и перенести данные из JSON:

```text
python -m db.import_json
```

SQL-схема находится в `sql/schema.sql`, готовые запросы предметной области —
в `sql/queries.sql`. В представлениях SQLite-результаты читаются как
`sqlite3.Row`, а пользовательские значения передаются в SQL через параметры
`?`.

Также `python main.py` запускает сервер разработки на `127.0.0.1:8000`.

После запуска откройте `http://127.0.0.1:8000/`. Перед первым запуском
примените миграции командой `python manage.py migrate`.

## Проверка

```text
python manage.py check
python manage.py test
python -m pytest -v
python -m flake8 .
```


## Загрузка и сохранение данных

Каталог `data/` содержит JSON-файл обмена данными. Экспорт выполняется для
конкретного дизайнера:

```text
python manage.py export_data anna
```

Загрузка выполняется обратно в SQLite:

```text
python manage.py import_data anna
```

Другой файл можно указать параметром `--file`. При ошибочном JSON или
неполных данных команда завершается с понятным сообщением об ошибке.

При экспорте объекты `Client`, `MoodboardCatalog` и `Moodboard` преобразуются
в обычные JSON-структуры. При импорте JSON обратно создаются экземпляры этих
классов, а связи мудборда с каталогом и клиентом восстанавливаются по имени и
email. JSON используется как формат обмена, основным хранилищем приложения
остаётся SQLite Django.

## План развития

- добавить изображения и элементы мудборда;
- подключить PostgreSQL;
- реализовать полноценные права доступа и публикацию портфолио;
- добавить API-документацию;
- настроить контейнеризацию и CI/CD.