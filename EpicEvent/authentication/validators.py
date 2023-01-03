from django.core.exceptions import ValidationError

class Validators:
    @staticmethod
    def check_letters_hyphen(data, field):
        for char in data:
            if not char.isalpha() and char != "-":
                raise ValidationError(f"Error in field <{field}>: Only letters and hyphen are authorized")

    @staticmethod
    def check_phone_number(data, field):
        for char in data:
            if not char.isnumeric():
                raise ValidationError(f"Error in field <{field}>: A phone number can contain only numbers !")