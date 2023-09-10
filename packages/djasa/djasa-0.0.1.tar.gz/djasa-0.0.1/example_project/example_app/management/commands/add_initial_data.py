from django.core.management.base import BaseCommand

from example_app.models import Book, BookSearchIntent


class Command(BaseCommand):
    help = 'Add initial data for Book and BookSearchIntent models.'

    def handle(self, *args, **kwargs):
        book_1 = Book(title="The Great Gatsby", author="F. Scott Fitzgerald", genre="Novel")
        book_2 = Book(title="Moby Dick", author="Herman Melville", genre="Novel")
        book_3 = Book(title="To Kill a Mockingbird", author="Harper Lee", genre="Novel")
        book_4 = Book(title="Pride and Prejudice", author="Jane Austen", genre="Romance")
        book_5 = Book(title="The Catcher in the Rye", author="J.D. Salinger", genre="Young Adult")
        Book.objects.bulk_create([book_1, book_2, book_3, book_4, book_5])

        training_phrases_1 = "Find me a book by [F. Scott Fitzgerald](author)\nLook for [The Great Gatsby](title)"
        training_phrases_2 = "Search for novels by [Herman Melville](author)\nDo you have [Moby Dick](title)?"

        intent_1 = BookSearchIntent(training_phrases=training_phrases_1)
        intent_2 = BookSearchIntent(training_phrases=training_phrases_2)
        intent_3 = BookSearchIntent(training_phrases="I want to read a romantic novel\nRecommend me a love story.")
        intent_4 = BookSearchIntent(training_phrases="Find books written by Jane Austen\nWhich books did she write?")
        intent_5 = BookSearchIntent(
            training_phrases="I need help finding a book for my teenager\nWhat young adult books do you recommend?")
        BookSearchIntent.objects.bulk_create([intent_1, intent_2, intent_3, intent_4, intent_5])
