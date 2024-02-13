from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.conf import settings
import os

class CustomUserManager(BaseUserManager):
    def create_user(self, username, role='user', tel_number='', address='', password=None, **extra_fields):
        if not username:
            raise ValueError('Username required!')
        user = self.model(username=username, role=role,tel_number=tel_number, address=address, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, role='admin', tel_number='', address='', password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, role, tel_number, address, password, **extra_fields)

def get_role():
    return {'admin': 'Admin', 'ofitsiant': 'Ofitsiant', 'user': 'User'}

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=get_role, default='user')
    tel_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.username
    
    def save(self, *args, **kwargs):
        if not self.password.startswith('pbkdf2_sha256$'): self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Image(models.Model):
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.id)

class Rate(models.Model):
    rate = models.IntegerField(default=5)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return str(self.rate)

def get_valyutas():
    return {'usd': 'Usd', 'som': "So'm", 'rubl': "rubl"}

class Food(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    price = models.IntegerField(default=0)
    valyuta = models.CharField(max_length=5, choices=get_valyutas, default='som')
    image = models.ManyToManyField(Image, blank=True)
    overal_rating = models.FloatField(default=0)
    overal_rated_users = models.IntegerField(default=0)
    ratings = models.ManyToManyField(Rate, blank=True)
    address_lat_a = models.FloatField(default=40.84116287658114)
    address_long_a = models.FloatField(default=72.32745981241342)
    description = models.TextField(max_length=1000, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    def delete(self, *args, **kwargs):
        for image in self.image.all():
            file_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
            if os.path.exists(file_path):
                os.remove(file_path)
            image.delete()
        super().delete(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    address_lat_a = models.FloatField(default=40.84411221242592)
    address_long_a = models.FloatField(default=72.33245510501874)
    estimate_date = models.IntegerField(default=30) # in minute
    delivered = models.BooleanField(default=False)
    food_on_the_way = models.BooleanField(default=False)
    assigned_officiant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    date = models.DateTimeField(auto_now_add=True)

def spacecomma(value):
    res = ''
    money = str(value)[::-1]
    for i in range(len(money)//3+1):
        res+=money[3*i:3*i+3]+' '
    return res.strip()[::-1] + " so'm"

class Delivered(models.Model):
    responsible = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    sold_number = models.IntegerField(default=0)
    total_income = models.BigIntegerField(default=0) # in so'm
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.food}: {spacecomma(self.total_income)}"

