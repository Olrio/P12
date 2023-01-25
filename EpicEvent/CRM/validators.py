from django.core.exceptions import ValidationError

def validate_amount(value):
    if type(value) is not float:
        raise ValidationError("Amount must be a float number !")