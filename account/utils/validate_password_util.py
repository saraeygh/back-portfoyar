from django.contrib.auth.password_validation import validate_password
from colorama import Fore, Style


def password_is_valid(password):
    try:
        validate_password(password)
        return True
    except Exception as e:
        print(Fore.RED)
        print(e)
        print(Style.RESET_ALL)
        return False
