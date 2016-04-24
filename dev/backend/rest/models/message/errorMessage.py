from django.db import models
from enum import Enum


class ErrorMessage(models.Model):
    id = models.AutoField(primary_key=True)
    error = models.CharField(max_length=200)
    http_code = models.IntegerField()

    def __unicode__(self):
        return self.error


class ErrorMessageType(Enum):

    REQUEST_CANNOT = 1
    INCORRECT_DATA = 2
    DISABLED_COOKIES = 3
    ALREADY_CONFIRMED = 4
    INVALID_TOKEN = 5
    USER_IN_USE = 6
    UNAUTHORIZED = 7
    INCORRECT_FILE_DATA = 8
    PASSWORD_LENGTH = 9
    NICK_LENGTH = 10
    EMAIL_INVALID = 11
    UNCONFIRMED_EMAIL = 12
    NOT_SIGNED_IN = 13
    NAME_LENGTH = 14
    INVALID_LEVEL = 15
    NOT_ALLOWED_METHOD = 16
