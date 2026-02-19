class LibraryException(Exception):
    def __init__(self, message: str):
        self.message = message


class NotFoundError(LibraryException): ...


class AlreadyExistsError(LibraryException): ...


class ActionForbiddenError(LibraryException): ...


class InvalidCredentialsError(LibraryException): ...
