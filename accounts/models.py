from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Die E-Mail Adresse muss angegeben werden")
        email = self.normalize_email(email)
        extra_fields.setdefault("username", email) # Bei einer normalen Registrierung wird die E-Mail auch als Benutzername eingetragen. Wenn die Entrypoint bereits einen Benutzernamen übergibt, bleibt dieser erhalten.
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        
        staff = extra_fields["is_staff"]
        if staff is not True:
            raise ValueError("Du hast keine Berechtigung")
        
        superuser = extra_fields["is_superuser"]
        if superuser is not True:
            raise ValueError("Du hast keine Berechtigung")
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(unique=True) # Anmeldefeld
    is_active = models.BooleanField(default=False)
    username = models.CharField(max_length=254, unique=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [] # Email und Passwort sind automatisch Pflicht
    
    def __str__(self):
        return self.email
    
    # Manager mit dem Model verbinden:
    # hier wird eine Instanz erstellt und dem Manager zugewiesen
    objects = CustomUserManager() 