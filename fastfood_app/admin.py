from django.contrib import admin
from .models import User, Image, Rate, Food, Order, Delivered

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'tel_number', 'address')

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'date')

class RateAdmin(admin.ModelAdmin):
    list_display = ('rate', 'user')

class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'valyuta', 'overal_rating', 'overal_rated_users')
    filter_horizontal = ('image', 'ratings')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'count', 'address_lat_a', 'address_long_a', 'estimate_date', 'assigned_officiant', 'delivered', 'food_on_the_way', 'date')

class DeliveredAdmin(admin.ModelAdmin):
    list_display = ('responsible', 'food', 'sold_number', 'total_income', 'date')

admin.site.register(User, UserAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Rate, RateAdmin)
admin.site.register(Food, FoodAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Delivered, DeliveredAdmin)
