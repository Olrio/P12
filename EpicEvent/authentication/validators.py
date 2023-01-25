from django.core.exceptions import ValidationError

class Validators:
    @staticmethod
    def check_letters_hyphen(data, field):
        for char in data:
            if not char.isalpha() and char != "-":
                raise ValidationError(f"<{field}>: Only letters and hyphen are authorized")

    @staticmethod
    def check_is_phone_number(data, field):
        for char in data:
            if not char.isnumeric():
                raise ValidationError(f"<{field}>: A phone number can contain only numbers !")

    @staticmethod
    def check_is_float(data, field):
        if type(data) is not float:
            raise ValidationError(f"<{field}>: This field must be a float number !")

    @staticmethod
    def contains_letters_and_numbers(data):
        alpha = False
        numeric = False
        for char in data:
            if char.isalpha():
                alpha = True
            if char.isnumeric():
                numeric = True
        if not alpha or not numeric:
            raise ValidationError("Password error : your password must contain letters and numbers")

    @staticmethod
    def has_8_length(data):
        if len(data) < 8:
            raise ValidationError("Password error : Your password must be at least 8 characters long!")

    @staticmethod
    def two_entries_differ(data1, data2):
        if data1 and data2 and data1 != data2:
            raise ValidationError("Password error : Your two entries for password differ !")

