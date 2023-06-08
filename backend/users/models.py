from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRoles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    SUPERUSER = 'superuser'


class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    role = models.CharField(
        max_length=10, choices=UserRoles.choices, default=UserRoles.USER)
    is_active = models.BooleanField(default=False)
    activation_code = models.CharField(max_length=20, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_groups",
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="customuser_user_permissions",
        verbose_name=('user permissions'),
    )

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_user(self):
        return self.role == UserRoles.USER

    @property
    def is_superuser(self):
        return super().is_superuser

    def set_role(self, new_role):
        if new_role in UserRoles.values:
            self.role = new_role
            self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='media/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
