def user_can_manage_builder(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)
