
# Create your models here.
# compte/models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, nom, password=None):
        if not email:
            raise ValueError("L'utilisateur doit avoir un email")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, password):
        user = self.create_user(email=email, nom=nom, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=150)
    nom   = models.CharField(max_length=100) # ↓ réduit un peu aussi
    date_inscription = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_inscription"]
