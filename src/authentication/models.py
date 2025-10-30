from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# ✅ Custom User Model (extend if needed)
class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


# ✅ Profile model (auto created with User)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
