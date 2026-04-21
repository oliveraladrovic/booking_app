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


class TimeSlotOccupiedError(DomainException):
    message: str = "Time slot already occupied"
    status_code: int = status.HTTP_409_CONFLICT


class InvalidStartTimeError(DomainException):
    message: str = "Start time can not be in past"
    status_code: int = status.HTTP_400_BAD_REQUEST


class BookingNotFoundError(DomainException):
    message: str = "Booking not found"
    status_code: int = status.HTTP_404_NOT_FOUND


class UnableToConfirmError(DomainException):
    message: str = "Only pending booking can be confirmed"
    status_code: int = status.HTTP_409_CONFLICT


class UnableToCancelError(DomainException):
    message: str = "Only pending and confirmed bookings can be canceled"
    status_code: int = status.HTTP_409_CONFLICT


class UnableToCompleteError(DomainException):
    message: str = "Only confirmed bookings can be completed"
    status_code: int = status.HTTP_409_CONFLICT


class BookingUpdateError(DomainException):
    message: str = "Only pending booking can be updated"
    status_code: int = status.HTTP_409_CONFLICT
