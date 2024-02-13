from rest_framework import serializers
from .models import User, Food, Image, Rate, Order, Delivered
from.calculations import get_distance, estimate_time


class UserControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'role', 'first_name', 'last_name', 'tel_number', 'address')


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'first_name', 'last_name', 'tel_number', 'address')


class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'tel_number', 'address')
        extra_kwargs = {
            'password': {'write_only': True},
        }


class EditUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user.
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'tel_number', 'address')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'image')


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = '__all__'


class FoodEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Food
        fields = ['id', 'name', 'price', 'valyuta', 'address_lat_a', 'address_long_a']


class FoodListSerializer(serializers.ModelSerializer):
    image = ImageSerializer(many=True, read_only=True)


    class Meta:
        model = Food
        fields = ['id', 'name', 'price', 'valyuta', 'overal_rating', 'overal_rated_users', 'address_lat_a', 'address_long_a', 'image']


class FoodCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Food
        fields = ['name', 'price', 'valyuta', 'address_lat_a', 'address_long_a', 'description', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        food = Food.objects.create(**validated_data)
        for image_data in images_data:
            try:
                image = Image.objects.create(image=image_data)
                food.image.add(image)
            except Exception as e:
                print(e)
        return food


class OfitsiantOrderSerializer(serializers.ModelSerializer):
    food = FoodListSerializer()

    class Meta:
        model = Order
        fields = ('id', 'user', 'food', 'count', 'address_lat_a', 'address_long_a', 'estimate_date', 'assigned_officiant', 'delivered', 'food_on_the_way', 'date')


class ListUserOrderSerializer(serializers.ModelSerializer):
    food = FoodListSerializer()

    class Meta:
        model = Order
        fields = ('id', 'user', 'food', 'count', 'address_lat_a', 'address_long_a', 'estimate_date', 'delivered', 'food_on_the_way', 'date')


class CreateUserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('food', 'count', 'address_lat_a', 'address_long_a')
        extra_kwargs = {
            'food': {'required': True},
            'count': {'required': True},
            'address_lat_a': {'required': True},
            'address_long_a': {'required': True},
        }
    
    def create(self, validated_data):
        food = validated_data['food']

        lat_b = food.address_lat_a
        long_b = food.address_long_a
        lat_a = validated_data['address_lat_a']
        long_a = validated_data['address_long_a']
        validated_data['user'] = self.context['request'].user
        distance = get_distance(lat_a, long_a, lat_b, long_b)
        validated_data['estimate_date'] = estimate_time(distance=distance, order_count=validated_data['count'])
        
        super().create(validated_data)        
        
        return validated_data['estimate_date']


class DeliveredSerializer(serializers.ModelSerializer):
    food = FoodListSerializer()
    class Meta:
        model = Delivered
        fields = ['id', 'responsible', 'sold_number', 'total_income', 'date', 'food']
