from apps.accounts.models import User

class UserFactory:
    @staticmethod
    def create_admin(username, password, email):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        user.role = 'admin'
        user.status = 'active'
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

    @staticmethod
    def create_staff(username, password, email):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        user.role = 'staff'
        user.status = 'pending'
        user.save()
        return user