from django.db import models
import asyncio
from concurrent.futures import ThreadPoolExecutor
from django.core import exceptions
from asgiref.sync import sync_to_async


class AsyncIter:
    """
    Async iterator for sync iterable
    """

    def __init__(self, iterable):
        self._iter = iter(iterable)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            element = next(self._iter)
        except StopIteration as e:
            raise StopAsyncIteration from e
        await asyncio.sleep(0)
        return element


class AsyncQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)

    def __aiter__(self):
        self._fetch_all()
        return AsyncIter(self._result_cache)

    def _fetch_all(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(super(AsyncQuerySet, self)._fetch_all)

    async def aall(self):
        return await sync_to_async(super().all)()

    async def afilter(self, *args, **kwargs):
        return await sync_to_async(super().filter)(*args, **kwargs)

    @staticmethod
    def _get_related_field_type(model, field_name):
        try:
            field = model._meta.get_field(field_name)
        except exceptions.FieldDoesNotExist:
            reverse_fields = [
                f
                for f in model._meta.get_fields()
                if f.is_relation and f.related_query_name() == field_name
            ]
            if reverse_fields:
                field = reverse_fields[0]
            else:
                raise exceptions.FieldError(
                    f"{field_name} does not exist on the model {model} or is not a related field."
                ) from None

        if isinstance(field, models.ForeignKey):
            return "select_related"
        elif isinstance(field, (models.ManyToManyField, models.OneToOneField)):
            return "prefetch_related"

        raise exceptions.FieldError(
            f"{field_name} on the model {model} is not a ForeignKey, ManyToManyField, or OneToOneField."
        ) from None

    def with_relation(self, *field_names):
        prefetch_fields = []
        select_fields = []

        for field_name in field_names:
            parts = field_name.split("__")
            model = self.model

            for part in parts:
                field_type = self._get_related_field_type(model, part)
                if field_type is None:
                    break

                if field_type == "select_related":
                    select_fields.append(field_name)
                    break
                elif field_type == "prefetch_related":
                    prefetch_fields.append(field_name)
                    break

                field = model._meta.get_field(part)
                if field.related_model:
                    model = field.related_model

        qs = self
        if select_fields:
            qs = qs.select_related(*select_fields)
        if prefetch_fields:
            qs = qs.prefetch_related(*prefetch_fields)
        return qs


class AsyncManager(models.Manager.from_queryset(AsyncQuerySet)):
    pass


class DjasaEntityManager(models.Manager):
    def extract_entity_types(self):
        entity_types = set()
        for entity in self.all():
            for field in entity.DjasaMeta.entities:
                entity_types.add(field)
        return list(entity_types)


class DjasaIntentManager(models.Manager):
    def extract_intent_examples(self):
        intent_examples = {}
        for intent_instance in self.all():
            intent_name = intent_instance.DjasaMeta.name
            phrases = intent_instance.training_phrases.replace(',', '\n').split('\n')
            if intent_name not in intent_examples:
                intent_examples[intent_name] = []
            intent_examples[intent_name].extend([phrase.strip() for phrase in phrases])
        return intent_examples
