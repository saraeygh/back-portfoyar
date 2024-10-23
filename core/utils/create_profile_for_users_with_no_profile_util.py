from django.contrib.auth.models import User
from account.models import Profile
from colorama import Fore, Style


def create_profile_for_users_with_no_profile():
    users_without_profiles = User.objects.filter(profile__isnull=True)

    for user in users_without_profiles:
        try:
            profile = Profile(user=user)
            profile.save()
            print(Fore.GREEN + f"Created profile for {user}" + Style.RESET_ALL)
        except Exception as e:
            print(
                Fore.RED
                + f"Error creating profile for {user}: {str(e)}"
                + Style.RESET_ALL
            )
