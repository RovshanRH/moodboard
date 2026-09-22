import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Client, Designer, Moodboard, MoodboardCatalog
from ..storage import export_data, import_data


class MoodboardApiTests(TestCase):
    def setUp(self) -> None:
        self.client_record = Client.objects.create(
            name="Студия Альфа",
            email="alpha@example.com",
        )
        response = self.client.post(
            "/api/auth/",
            data={
                "username": "designer",
                "password": "strong-password",
                "display_name": "Анна Дизайнер",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.catalog = MoodboardCatalog.objects.create(
            designer=Designer.objects.get(user__username="designer"),
            name="Брендинг",
        )

    def test_moodboard_creation_and_listing(self) -> None:
        response = self.client.post(
            "/api/moodboards/",
            data={
                "title": "Новый бренд",
                "description": "Референсы для айдентики",
                "catalog_id": self.catalog.id,
                "client_id": self.client_record.id,
                "background_color": "#112233",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Moodboard.objects.count(), 1)
        self.assertEqual(response.json()["catalog"]["name"], "Брендинг")

        response = self.client.get("/api/moodboards/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 1)

    def test_export_returns_png(self) -> None:
        board = Moodboard.objects.create(
            designer=Designer.objects.get(user__username="designer"),
            title="Экспорт",
        )
        response = self.client.get(f"/api/moodboards/{board.id}/export/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_authentication_is_required(self) -> None:
        self.client.post(
            "/api/auth/",
            data={},
            content_type="application/json",
        )
        self.client.logout()
        response = self.client.get("/api/moodboards/")
        self.assertEqual(response.status_code, 401)

    def test_invalid_input_returns_bad_request(self) -> None:
        response = self.client.post(
            "/api/moodboards/",
            data={"title": 42},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/moodboards/",
            data={"title": "Некорректный цвет", "background_color": "red"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_json_export_and_import(self) -> None:
        designer = Designer.objects.get(user__username="designer")
        Moodboard.objects.create(
            designer=designer,
            catalog=self.catalog,
            client=self.client_record,
            title="Импортируемый мудборд",
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "moodboards.json"
            export_data(designer, path)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(payload["moodboards"][0]["title"], "Импортируемый мудборд")

            Moodboard.objects.all().delete()
            imported = import_data(designer, path)

        self.assertEqual(imported, 1)
        self.assertEqual(Moodboard.objects.get().title, "Импортируемый мудборд")

    def test_domain_objects_expose_behavior(self) -> None:
        designer = Designer.objects.get(user__username="designer")
        board = Moodboard(
            designer=designer,
            title="Объектная модель",
            background_color="#112233",
        )

        self.assertEqual(str(designer), "Анна Дизайнер")
        self.assertEqual(str(self.client_record), "Студия Альфа")
        self.assertEqual(str(self.catalog), "Брендинг")
        self.assertTrue(designer.owns_catalog(self.catalog))
        self.assertTrue(self.catalog.belongs_to(designer))
        self.assertTrue(board.can_use_catalog(self.catalog))

        board.assign_catalog(self.catalog)
        board.assign_client(self.client_record)
        board.change_background("#AABBCC")
        data = board.to_data()

        self.assertEqual(data["catalog"], "Брендинг")
        self.assertEqual(data["client_email"], "alpha@example.com")
        self.assertEqual(data["background_color"], "#AABBCC")

    def test_board_rejects_foreign_catalog(self) -> None:
        other_user = Designer.objects.create(
            user=User.objects.create_user(
                username="other",
                password="strong-password",
            ),
            display_name="Другой дизайнер",
        )
        foreign_catalog = MoodboardCatalog.objects.create(
            designer=other_user,
            name="Чужой каталог",
        )
        board = Moodboard(
            designer=Designer.objects.get(user__username="designer"),
            title="Проверка доступа",
        )

        with self.assertRaises(ValueError):
            board.assign_catalog(foreign_catalog)
