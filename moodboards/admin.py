from django.contrib import admin

from .models import Client, Designer, Moodboard, MoodboardCatalog


admin.site.register(Designer)
admin.site.register(Client)
admin.site.register(MoodboardCatalog)
admin.site.register(Moodboard)
