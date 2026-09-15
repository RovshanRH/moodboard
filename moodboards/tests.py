from django.test import TestCase

from .models import Client, Designer, Moodboard, MoodboardCatalog


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
        response = self.client.get(
            f"/api/moodboards/{board.id}/export/"
        )
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
