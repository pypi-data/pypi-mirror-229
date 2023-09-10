from djasa.models import DjasaEntity, DjasaIntent
from django.db import models


class Book(DjasaEntity):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class DjasaMeta:
        entities = ["title", "author", "genre"]


class BookSearchIntent(DjasaIntent):
    class DjasaMeta:
        name = "search_book"

    def __str__(self):
        return self.training_phrases
