from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class UserRoles(models.TextChoices):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    # SUPERUSER = 'superuser'


class User(AbstractUser):
    """
    This model represents users. Each user can belong to multiple groups and
    have a specific role within each group (user, moderator, or admin).
    """
    email = models.EmailField(unique=True)
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

    def is_moderator_in_any_group(self):
        return self.user_group_roles.filter(role=UserRoles.MODERATOR).exists()

    def is_admin_in_any_group(self):
        return self.user_group_roles.filter(role=UserRoles.ADMIN).exists()

    def is_user_in_any_group(self):
        return self.user_group_roles.filter(role=UserRoles.USER).exists()

    def get_role_in_group(self, group):
        return self.user_group_roles.get(group=group).role if self.user_group_roles.filter(group=group).exists() else None

    def has_permission(self, permission_codename):
        """
        Check if the user has a specific permission.
        """
        if self.user_permissions.filter(codename=permission_codename).exists():
            return True

        for group in self.groups.all():
            if group.permissions.filter(codename=permission_codename).exists():
                return True

        return False


class UserProfile(models.Model):
    """
    This model represents additional information about the User,
    including profile picture, birth date, and phone number.
    Each user has one associated profile.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='media/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} profile'


class UserGroupRole(models.Model):
    """
    This model represents the many-to-many relationship between a User and a Group.
    Each row represents a specific role that a user has within a group. 
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_group_roles')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=10, choices=UserRoles.choices, default=UserRoles.USER)

    class Meta:
        unique_together = ('user', 'group')
        verbose_name = 'User Group Role'
        verbose_name_plural = 'User Group Roles'

    def add_role(self, group, role):
        """
        Add a role for the user in a specific group.
        """
        UserGroupRole.objects.create(user=self, group=group, role=role)

    def remove_role(self, group):
        """
        Remove a role for the user in a specific group.
        """
        UserGroupRole.objects.filter(user=self, group=group).delete()

    def change_role(self, group, role):
        """
        Change the user's role in a specific group.
        """
        UserGroupRole.objects.filter(user=self, group=group).update(role=role)

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN

    @property
    def is_moderator(self):
        return self.role == UserRoles.MODERATOR

    @property
    def is_user(self):
        return self.role == UserRoles.USER

    def __str__(self):
        return f'{self.user.username} - {self.group.name} - {self.role}'
