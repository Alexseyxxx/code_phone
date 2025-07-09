from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from users.utils import generate_invite_code  


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Телефон обязателен')
        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()  
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)
    is_verified = models.BooleanField(default=False)
    invite_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    used_invite_code = models.CharField(max_length=6, null=True, blank=True)
    invited_users = models.ManyToManyField('self', symmetrical=False, related_name='invited_by', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = generate_invite_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone


class AuthCode(models.Model):
    phone = models.CharField(max_length=15)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.phone} → {self.code}'

    class Meta:
        ordering = ['-created_at']
