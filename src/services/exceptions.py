from rest_framework.exceptions import APIException


class ValidationError(APIException):
    def __int__(self, message):
        self.message = message
