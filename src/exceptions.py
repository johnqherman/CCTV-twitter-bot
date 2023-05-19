class FetchCamerasException(Exception):
    """Custom exception class for handling errors when fetching camera links."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)


class SaveImageException(Exception):
    """Custom exception class for handling errors when saving camera images."""

    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)
