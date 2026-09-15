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
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── main.py
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
```

## План развития

- добавить изображения и элементы мудборда;
- подключить PostgreSQL;
- реализовать полноценные права доступа и публикацию портфолио;
- добавить API-документацию;
- настроить контейнеризацию и CI/CD.