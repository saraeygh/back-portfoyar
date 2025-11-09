from django.contrib.auth.password_validation import validate_password


def password_is_valid(password):
    try:
        validate_password(password)
        return True
    except Exception as e:
        print(e)
        return False
