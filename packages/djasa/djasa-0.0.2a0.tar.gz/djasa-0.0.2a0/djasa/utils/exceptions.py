class DjasaException(Exception):
    """Base class for Djasa exceptions."""
    pass


class InvalidRasaURL(DjasaException):
    """Raised when the Rasa URL is invalid."""
    pass
