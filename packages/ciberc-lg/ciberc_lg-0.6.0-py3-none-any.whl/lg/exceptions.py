"""Exception module"""


class LGException(Exception):
    """Base exception for LG. Catch all LG exceptions"""
    def __init__(self, message: str) -> None:
        """
        Args:
            message: A message describing the exception.
        """
        self.message = message
        super().__init__(message)


class StatusError(LGException):
    def __init__(self, status: str, message: str) -> None:
        _message = f'status={status}. {message}'
        super().__init__(_message)
