from __future__ import annotations

from django import forms

from accounts.models import Client
from catalogs.models import MoodboardCatalog

from .models import Moodboard


class MoodboardSearchForm(forms.Form):
    q = forms.CharField(
        max_length=160,
        required=False,
        label="Название",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Название мудборда",
            }
        ),
    )


class MoodboardForm(forms.ModelForm):
    class Meta:
        model = Moodboard
        fields = [
            "title",
            "description",
            "background_color",
            "palette",
            "catalog",
            "client",
            "image",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control mb-3", "maxlength": 160}
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control mb-3", "rows": 4}
            ),
            "background_color": forms.TextInput(
                attrs={
                    "class": "form-control form-control-color mb-3",
                    "type": "color",
                }
            ),
            "palette": forms.TextInput(
                attrs={
                    "class": "form-control mb-3",
                    "placeholder": "#112233, #AABBCC",
                }
            ),
            "catalog": forms.Select(attrs={"class": "form-select mb-3"}),
            "client": forms.Select(attrs={"class": "form-select mb-3"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control mb-3"}),
        }
        help_texts = {
            "palette": "Укажите HEX-цвета через запятую.",
            "image": "Загрузите изображение для обложки мудборда.",
        }

    def __init__(self, designer=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["catalog"].empty_label = "Без каталога"
        self.fields["client"].empty_label = "Без заказчика"
        self.fields["client"].queryset = Client.objects.all().order_by("name")

        if designer is not None:
            self.fields["catalog"].queryset = MoodboardCatalog.objects.filter(
                designer=designer
            ).order_by("name")
        else:
            self.fields["catalog"].queryset = MoodboardCatalog.objects.none()

        if not self.initial.get("background_color"):
            self.initial["background_color"] = "#F4EFE6"

    def clean_palette(self):
        palette = self.cleaned_data.get("palette")
        if palette in (None, ""):
            return []
        if isinstance(palette, str):
            palette = [
                color.strip()
                for color in palette.split(",")
                if color.strip()
            ]
        if not isinstance(palette, list):
            raise forms.ValidationError("Палитра должна быть списком цветов.")
        cleaned: list[str] = []
        for color in palette:
            if not isinstance(color, str):
                raise forms.ValidationError("Каждый цвет должен быть строкой.")
            value = color.strip()
            if value:
                cleaned.append(value)
        return cleaned

    def save(self, commit: bool = True):
        instance = super().save(commit=False)
        instance.palette = self.cleaned_data.get("palette", [])
        if commit:
            instance.save()
        return instance


MoodboardFilterForm = MoodboardSearchForm

__all__ = ["MoodboardForm", "MoodboardSearchForm", "MoodboardFilterForm"]
