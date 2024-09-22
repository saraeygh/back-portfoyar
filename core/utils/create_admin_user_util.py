from django.contrib.auth.models import User

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123456Admin"
ADMIN_FIRST_NAME = "ادمین"
ADMIN_LAST_NAME = ""


def create_admin_user():

    user = User.objects.filter(username=ADMIN_USERNAME)
    if not user.exists():
        admin_user = User.objects.create_superuser(
            username=ADMIN_USERNAME,
            password=ADMIN_PASSWORD,
            first_name=ADMIN_FIRST_NAME,
            last_name=ADMIN_LAST_NAME,
        )
        print("Admin user created.")
    else:
        print("Admin user already exists.")
