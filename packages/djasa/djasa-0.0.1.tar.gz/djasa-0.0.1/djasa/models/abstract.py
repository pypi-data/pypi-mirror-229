from django.db import models
from django.core.exceptions import FieldDoesNotExist

from djasa.models.manager import DjasaEntityManager, DjasaIntentManager, AsyncManager


class DjasaBaseModel(models.Model):
    """
    Abstract base model for all Djasa models.
    """
    aobjects = AsyncManager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._djasa_meta = self.get_djasa_meta()

    @classmethod
    def get_djasa_meta(cls):
        """
        Retrieve and validate the DjasaMeta class for the current Djasa model.
        Raises appropriate exceptions for missing or invalid fields.
        """
        djasa_meta = cls._retrieve_djasa_meta()
        cls._validate_djasa_meta_fields(djasa_meta)
        return djasa_meta

    @classmethod
    def _retrieve_djasa_meta(cls):
        """
        Retrieve the DjasaMeta class from the current Djasa model.
        Raises an exception if DjasaMeta is not defined.
        """
        djasa_meta = getattr(cls, "DjasaMeta", None)
        if not djasa_meta:
            raise NotImplementedError(f"Subclasses of {cls.__name__} must define 'DjasaMeta'.")
        return djasa_meta

    @classmethod
    def _validate_djasa_meta_fields(cls, djasa_meta):
        """
        Abstract method to validate the presence of required fields in the DjasaMeta class.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class DjasaEntity(DjasaBaseModel):
    """
    Abstract model for Djasa entities. Entities must provide a 'DjasaMeta' with
    an 'entities' list or tuple.
    """
    objects = DjasaEntityManager()

    class Meta:
        abstract = True

    @classmethod
    def _validate_djasa_meta_fields(cls, djasa_meta):
        entities = getattr(djasa_meta, "entities", None)
        if not entities or not isinstance(entities, (list, tuple)):
            raise FieldDoesNotExist("DjasaMeta must define 'entities' as a list or tuple.")
        for entity in entities:
            if not hasattr(cls, entity):
                raise FieldDoesNotExist(f"Model must define '{entity}'.")


class DjasaIntent(DjasaBaseModel):
    """
    Abstract model for Djasa intents. Intents must provide a 'DjasaMeta' with
    a 'name' for the intent.
    """
    objects = DjasaIntentManager()

    class Meta:
        abstract = True

    training_phrases = models.TextField(help_text="Enter training phrases, one per line.")

    @classmethod
    def _validate_djasa_meta_fields(cls, djasa_meta):
        if not hasattr(djasa_meta, "name"):
            raise FieldDoesNotExist("DjasaMeta must define 'name' for the intent.")
