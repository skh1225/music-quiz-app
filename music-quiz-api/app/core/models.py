"""
Database models.
"""
from typing import Any, Dict, Tuple
import uuid
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField


def music_audio_file_path(instance, filename):
    """Generate file path for new recipe audio."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'audio', filename)

def music_image_file_path(instance, filename):
    """Generate file path for new recipe audio."""
    filename = os.path.split(filename)[1]

    return os.path.join('uploads', 'image', filename)


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, name=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        if not name:
            raise ValueError('User must have a name.')
        user = self.model(email=self.normalize_email(email), name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, name):
        """Create and return a new superuser."""
        user = self.create_user(email, password, name)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class Room(models.Model):
    """Singer object."""
    name = models.CharField(max_length=255, primary_key=True)
    password = models.CharField(max_length=255, blank=True)
    music_tags = models.CharField(max_length=255, blank=True)
    is_team_battle = models.BooleanField(default=False)
    is_full = models.BooleanField(default=False)
    max_user = models.IntegerField(validators=[MinValueValidator(1),
                                               MaxValueValidator(8)], default=6)
    music_list = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    music_length = models.IntegerField(validators=[MinValueValidator(1),
                                               MaxValueValidator(100)])

    def __str__(self):
        return self.name

class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    room_name = models.CharField(max_length=255, blank=True)
    channel_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    REQUIRED_FIELDS = ['name']
    USERNAME_FIELD = 'email'


class Music(models.Model):
    """Music object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    singers = models.ManyToManyField('Singer', blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    running_time = models.IntegerField(null=True, blank=True)
    released_year = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    image = models.URLField(max_length=255, null=True, blank=True)
    image_file = models.FileField(null=True, upload_to=music_image_file_path)
    audio = models.FileField(null=True, upload_to=music_audio_file_path)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def delete(self, *args, **kargs):
        if self.audio:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.audio.path))
        if self.image_file:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.image_file.path))
        super(Music, self).delete(*args, **kargs)


    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag object."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Singer(models.Model):
    """Singer object."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

