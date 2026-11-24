class DomainError(Exception):
    """Base class for errors the application knows how to explain to a client."""


class InvalidReviewError(DomainError):
    """The review text cannot be classified (empty, too long...)."""


class BatchTooLargeError(DomainError):
    """Too many reviews in a single batch request."""


class ModelNotAvailableError(DomainError):
    """No trained model could be loaded."""
