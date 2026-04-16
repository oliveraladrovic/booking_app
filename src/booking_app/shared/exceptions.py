class DomainException(Exception):
    message: str = "Domain Error"


class EmailAlreadyExistsError(DomainException):
    message: str = "Email already exists"
