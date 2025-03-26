class IdExistsError(ValueError):
    """Raised when a prior existing model with a specified id is found."""


class IdNotFoundError(ValueError):
    """Raised when a model with a specified id is not found."""
