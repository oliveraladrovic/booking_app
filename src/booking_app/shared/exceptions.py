from fastapi import status


class DomainException(Exception):
    message: str = "Domain Error"
    status_code: int = status.HTTP_400_BAD_REQUEST


class EmailAlreadyExistsError(DomainException):
    message: str = "Email already exists"
    status_code: int = status.HTTP_409_CONFLICT


class UserNotFoundError(DomainException):
    message: str = "User not found"
    status_code: int = status.HTTP_404_NOT_FOUND


class ServiceNotFoundError(DomainException):
    message: str = "Service not found"
    status_code: int = status.HTTP_404_NOT_FOUND
