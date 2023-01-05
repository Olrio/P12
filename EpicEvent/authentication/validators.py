from django.core.exceptions import ValidationError
from CRM.models import Contract

class Validators:
    @staticmethod
    def check_letters_hyphen(data, field):
        for char in data:
            if not char.isalpha() and char != "-":
                raise ValidationError(f"Error in field <{field}>: Only letters and hyphen are authorized")

    @staticmethod
    def check_is_phone_number(data, field):
        for char in data:
            if not char.isnumeric():
                raise ValidationError(f"Error in field <{field}>: A phone number can contain only numbers !")

    @staticmethod
    def check_is_float(data, field):
        if type(data) is not float:
            raise ValidationError(f"Error in field <{field}>: This field must be a float number !")
