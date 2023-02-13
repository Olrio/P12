from django.core.exceptions import ValidationError
from authentication.models import User

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
    def is_valid_password(data):
        errors = list()
        alpha = False
        numeric = False
        for char in data:
            if char.isalpha():
                alpha = True
            if char.isnumeric():
                numeric = True
        if not alpha or not numeric:
            errors.append("Password error : your password must contain letters and numbers")
        if len(data) < 8:
            errors.append("Password error : Your password must be at least 8 characters long!")
        if errors:
            raise ValidationError(errors)

    @staticmethod
    def two_entries_differ(data1, data2):
        if data1 and data2 and data1 != data2:
            raise ValidationError("Password error : Your two entries for password differ !")

    @staticmethod
    def is_valid_team(data):
        if data not in ['Management', 'Sales', 'Support']:
            raise ValidationError("<Team>: Team must be one of these : Management, Sales or Support")

    @staticmethod
    def is_prior_to_created_date(due, created):
        if due.date() < created.date():
            raise ValidationError("Payment due date can't be prior to creation date")

    @staticmethod
    def is_valid_username(first_name, last_name):
        # let's set the username from first_name and last_name
        # it's the lower first(s) letter(s) of first_name completed with the lower last_name
        # if this username already exists, a number is added, starting from 2
        initials = ''.join([name[0] for name in first_name.split("-")])
        counter = 2
        if User.objects.filter(username=initials.lower() + last_name.lower()).exists():
            while True:
                if User.objects.filter(
                        username=initials.lower() + last_name.lower() + str(counter)).exists():
                    counter += 1
                else:
                    break
            username = initials.lower() + last_name.lower() + str(counter)
        else:
            username = initials.lower() + last_name.lower()
        return username
