from fastapi import status


class DomainException(Exception):
    message: str = "Domain Error"
    status_code: int = status.HTTP_400_BAD_REQUEST


class EmailAlreadyExistsError(DomainException):
    message: str = "Email already exists"
    status_code: int = status.HTTP_409_CONFLICT
