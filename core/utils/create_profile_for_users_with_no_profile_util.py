from django.contrib.auth.models import User
from account.models import Profile


def create_profile_for_users_with_no_profile():
    users_without_profiles = User.objects.filter(profile__isnull=True)

    for user in users_without_profiles:
        try:
            profile = Profile(user=user)
            profile.save()
            print(f"Created profile for {user}")
        except Exception as e:
            print(f"Error creating profile for {user}: {str(e)}")
