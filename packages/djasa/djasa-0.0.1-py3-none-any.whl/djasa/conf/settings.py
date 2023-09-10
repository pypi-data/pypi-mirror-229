from django.apps import apps
from django.conf import settings

from djasa.models import DjasaEntity, DjasaIntent
from djasa.utils.exceptions import InvalidRasaURL
from django.core.exceptions import ImproperlyConfigured


class DjasaSettings:
    def __init__(self):
        self.RASA_SERVER_URL: str = getattr(settings, 'DJASA_RASA_SERVER_URL', "http://localhost:5005")
        self.RASA_ACTION_SERVER_URL: str = getattr(settings, 'DJASA_RASA_ACTION_SERVER_URL', "http://localhost:5055")
        self.RASA_TRAINING_ENDPOINT: str = f"{self.RASA_SERVER_URL}/model/train"
        self.RASA_WEBHOOK_ENDPOINT: str = f"{self.RASA_SERVER_URL}/webhooks/rest/webhook"
        self.RASA_MODEL_ENDPOINT: str = f"{self.RASA_SERVER_URL}/model"
        self.DJASA_ENTITIES: list = []
        self.DJASA_INTENTS: list = []
        self.populate_entities()
        self.populate_intents()
        self.validate()

    def validate(self):
        # Validate RASA_SERVER_URL
        if not self.RASA_SERVER_URL.startswith("http"):
            raise InvalidRasaURL("Invalid RASA_SERVER_URL. It should start with http or https.")

    def populate_entities(self):
        self.DJASA_ENTITIES = [model for model in apps.get_models() if issubclass(model, DjasaEntity)]

    def populate_intents(self):
        self.DJASA_INTENTS = [model for model in apps.get_models() if issubclass(model, DjasaIntent)]

    def get_model(self, model_name: str):
        """
        Returns the Django model corresponding to the provided model name from the DJASA_ENTITIES.
        """
        for model in self.DJASA_ENTITIES:
            if model.__name__ == model_name:
                return model
        raise ImproperlyConfigured(f"Model named {model_name} is not registered as a DjasaEntity.")
