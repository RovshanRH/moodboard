# Mood board creator

Веб-бэкенд конструктора мудбордов для дизайнеров, фрилансеров и творческих
команд. Проект реализован на Django и использует SQLite для локальной разработки.

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

Регистрация дизайнера создаёт пользователя Django, профиль `Designer` и сессию:

```http
POST /api/auth/
Content-Type: application/json

{
	"username": "anna",
	"password": "strong-password",
	"display_name": "Анна Дизайнер"
}
```

Выход выполняется запросом `DELETE /api/auth/`.

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

```text
moodboard/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── moodboards/
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
├── main.py
├── data/
│   └── moodboards.json
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

Также `python main.py` запускает сервер разработки на `127.0.0.1:8000`.

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