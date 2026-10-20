from django.contrib import admin

from accounts.models import Client, Designer
from boards.models import Moodboard
from catalogs.models import MoodboardCatalog


admin.site.register(Designer)
admin.site.register(Client)
admin.site.register(MoodboardCatalog)
admin.site.register(Moodboard)
