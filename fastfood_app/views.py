from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .serializers import (
    UserControlSerializer,
    UserInfoSerializer,
    CreateUserSerializer,
    EditUserSerializer,
    FoodListSerializer,
    FoodCreateSerializer,
    FoodEditSerializer,
    OfitsiantOrderSerializer,
    ListUserOrderSerializer,
    CreateUserOrderSerializer,
    ListUserOrderSerializer,
    DeliveredSerializer,
)
from .models import User, Food, Order, Delivered, Rate
from .filters import DeliveredFilter
from .calculations import change_estimates


# Admin
class IsAdminUser(BasePermission):
    """
    Custom permission to allow only admin users.
    """
    def has_permission(self, request, view):
        try:
            return bool(request.user.role in ['admin'])
        except: return False


class UserControlView(viewsets.ModelViewSet):
    """
    Controls user-related operations accessible only to administrators.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    serializer_class = UserControlSerializer
    queryset = User.objects.all()


class DeliveredModelViewSet(viewsets.ModelViewSet):
    """
    Allows administrators to manage Delivered objects, including filtering by year and month.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Delivered.objects.all()
    serializer_class = DeliveredSerializer
    filterset_class = DeliveredFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if year and month:
            queryset = queryset.filter(date__year=year, date__month=month)
        return queryset


# Ofisant
class IsAdminOrOfitsiantUser(BasePermission):
    """
    Custom permission to allow only admin or ofitsiant users to create foods.
    """
    def has_permission(self, request, view):
        try:
            return bool(request.user.role in ['ofitsiant', 'admin'])
        except: return False


class FoodCreateAPIView(APIView):
    """
    Handles the creation of food items through API requests.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrOfitsiantUser]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @extend_schema(request=FoodCreateSerializer, responses=FoodCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = FoodCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FoodUpdateAPIView(APIView):
    """
    Handles the updating of food items through API requests.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrOfitsiantUser]

    @extend_schema(request=FoodEditSerializer, responses=FoodEditSerializer)
    def put(self, request, id):
        try:
            food = Food.objects.get(id=id)
            serializer = FoodEditSerializer(food, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Food.DoesNotExist:
            return Response({"message": "Food not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class FoodDeleteAPIView(APIView):
    """
    Handles the deletion of food items through API requests.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None

    def delete(self, request, id):
        try:
            food = Food.objects.get(id=id)
            food.delete()
        except Food.DoesNotExist:
            return Response({"message": "Food not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"message": "Food deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class OfitsiantOrderListAPIView(APIView):
    """
    API endpoint for officiants to view unassigned orders.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None

    def get(self, request):
        orders = Order.objects.filter(assigned_officiant__isnull=True, delivered=False)
        serializer = OfitsiantOrderSerializer(orders, many=True)
        return Response(serializer.data)


class OfitsiantOrderAssignedListAPIView(APIView):
    """
    API endpoint for officiants to view unassigned orders.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None
    
    def get(self, request):
        orders = Order.objects.filter(assigned_officiant=request.user, delivered=False)
        serializer = OfitsiantOrderSerializer(orders, many=True)
        return Response(serializer.data)


class OfitsiantOrderAcceptAPIView(APIView):
    """
    API endpoint for officiants to accept orders.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None
    
    def put(self, request, id):
        try:
            order = Order.objects.get(id=id, delivered=False, food_on_the_way=False, assigned_officiant__isnull=True)
            order.assigned_officiant = request.user
            order.save()
            return Response({"message": "Order accepted successfully"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found or already assigned"}, status=status.HTTP_404_NOT_FOUND)


class OfitsiantOrderOnTheWayAPIView(APIView):
    """
    API endpoint for officiants to mark orders as delivered.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None
    
    def put(self, request, id):
        try:
            order = Order.objects.get(id=id, assigned_officiant=request.user, delivered=False, food_on_the_way=False)
            order.food_on_the_way = True
            order.save()
            return Response({"message": "Order is on the way"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found or not assigned to you"}, status=status.HTTP_404_NOT_FOUND)


class OfitsiantOrderDeliverAPIView(APIView):
    """
    API endpoint for officiants to mark orders as delivered.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrOfitsiantUser]
    serializer_class = None
    
    def put(self, request, id):
        try:
            order = Order.objects.get(id=id, assigned_officiant=request.user, delivered=False)
            valyuta = order.food.valyuta
            if valyuta == 'usd':
                totat_income = int(order.food.price*order.count*12348.14)
            elif valyuta == 'rubl':
                totat_income = int(order.food.price*order.count*135.46)
            else:
                totat_income = order.food.price*order.count
            Delivered.objects.create(
                responsible=request.user,
                food=order.food,
                sold_number=order.count,
                total_income=totat_income
            )

            order.delete()
            return Response({"message": "Order delivered successfully"}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found or not assigned to you"}, status=status.HTTP_404_NOT_FOUND)


class OfitsiantDeliveredAPIView(APIView):
    """
    Allows ofitsiant to manage Delivered objects, including filtering by year and month.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminOrOfitsiantUser]
    serializer_class = DeliveredSerializer

    def get(self, request, month, year):
        try:
            user = request.user
            delivered_objects = Delivered.objects.filter(responsible=user, date__year=year, date__month=month)
            serializer = self.serializer_class(delivered_objects, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


# Apis for Users
class UserInfoAPIView(APIView):
    """
    Handles requests related to user information.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserInfoSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class UserRegistrationAPIView(APIView):
    """
    API endpoint for registering new users.
    
    HTTP Methods Allowed: POST
    """
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses=CreateUserSerializer)
    def post(self, request, format=None):
        try:
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            username = serializer.validated_data.get('username')
            if User.objects.filter(username=username).exists():
                return Response({"message": "This username is already in use. Please choose a different one."},
                                status=status.HTTP_400_BAD_REQUEST)

            password = request.data.get('password')
            try:
                validate_password(password)
            except ValidationError as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": f"User created successfully {user.username}",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class UserInfoEditAPIView(APIView):
    """
    API endpoint for editing user information.
    
    HTTP Methods Allowed: PUT
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=EditUserSerializer, responses=EditUserSerializer)
    def put(self, request):
        try:
            user = request.user
            serializer = EditUserSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Server error {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        

class UserDeleteAPIView(APIView):
    """
    API endpoint for deleting user account.
    
    HTTP Methods Allowed: DELETE
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def delete(self, request):
        try:
            user = request.user
            user.delete()
            return Response({"message": "User account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    """
    def post(self, request):
        return Response({"message": "No server-side logout required."})


class FoodListAPIView(APIView):
    """
    Handles requests to retrieve a list of foods.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = FoodListSerializer

    def get(self, request):
        foods = Food.objects.all()
        serializer = FoodListSerializer(foods, many=True)
        return Response(serializer.data)


class RateFoodAPIView(APIView):
    """
    API view to rate a food item.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = None

    def put(self, request, id, rate):
        try:
            food = Food.objects.get(id=id)
            user = request.user
            try:
                rate_item = food.ratings.get(user=user)
                old_rate = rate_item.rate
                obj = Rate.objects.get(id=rate_item.id)
                obj.rate = rate
                obj.save()
                food.overal_rating = (food.overal_rating * food.overal_rated_users - old_rate + rate) / food.overal_rated_users
                food.save()
            except:
                obj = Rate.objects.create(rate=rate, user=user)
                food.ratings.add(obj)
                food.overal_rating = (food.overal_rating * food.overal_rated_users + rate) / (food.overal_rated_users + 1)
                food.overal_rated_users += 1
                food.save()

            serializer = FoodListSerializer(Food.objects.get(id=id))
            return Response(serializer.data)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrderCreateAPIView(APIView):
    """
    API endpoint for creating orders.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(request=CreateUserOrderSerializer, responses=CreateUserOrderSerializer)
    def post(self, request):
        serializer = CreateUserOrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            estimate_date = serializer.save()
            response_data = {
                'order': serializer.data,
                'estimate_date': estimate_date
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserOrdersAPIView(APIView):
    """
    API endpoint for retrieving a list of MyModel objects.
    """
    serializer_class = None

    def get(self, request):
        queryset = Order.objects.filter(user=request.user)
        serializer = ListUserOrderSerializer(queryset, many=True)
        return Response(serializer.data)


class UserOrderDeleteAPIView(APIView):
    """
    API endpoint for deleting an order.
    """
    serializer_class = None

    def delete(self, request, id):
        try:
            order = Order.objects.get(id=id, user=request.user)
            order.delete()
            change_estimates(order)
            return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"Server error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
