from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserInfoAPIView,
    UserRegistrationAPIView,
    UserInfoEditAPIView,
    UserDeleteAPIView,
    UserControlView,
    UserOrderCreateAPIView,
    UserOrdersAPIView,
    UserOrderDeleteAPIView,
    FoodListAPIView,
    FoodCreateAPIView,
    FoodUpdateAPIView,
    FoodDeleteAPIView,
    OfitsiantOrderListAPIView,
    OfitsiantOrderAssignedListAPIView,
    OfitsiantOrderAcceptAPIView,
    OfitsiantOrderOnTheWayAPIView,
    OfitsiantOrderDeliverAPIView,
    DeliveredModelViewSet,
    OfitsiantDeliveredAPIView,
    RateFoodAPIView,
)

from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)

router = DefaultRouter()
router.register('user', UserControlView, basename='user')
router.register('deliver', DeliveredModelViewSet, basename='deliver')

urlpatterns = [
    # account
    path('account/register/', UserRegistrationAPIView.as_view(), name='user-registration'),
    path('account/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('account/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('account/info/', UserInfoAPIView.as_view(), name='user-info'),
    path('account/edit/', UserInfoEditAPIView.as_view(), name='user-info-edit'),
    path('account/delete/', UserDeleteAPIView.as_view(), name='user-delete'),
    
    # admin
    path('admin/', include(router.urls)),

    # ofissant
    path('ofitsiant/foods/post/', FoodCreateAPIView.as_view(), name='food-create'),
    path('ofitsiant/foods/get/', FoodListAPIView.as_view(), name='ofisant-food-list'),
    path('ofitsiant/foods/put/<int:id>/', FoodUpdateAPIView.as_view(), name='ofisant-food-edit'),
    path('ofitsiant/foods/delete/<int:id>/', FoodDeleteAPIView.as_view(), name='ofisant-food-delete'),
    path('ofitsiant/orders/get/', OfitsiantOrderListAPIView.as_view(), name='order-get'),
    path('ofitsiant/orders-assigned/get/', OfitsiantOrderAssignedListAPIView.as_view(), name='order-get-assigned'),
    path('ofitsiant/order/accept/put/<int:id>/', OfitsiantOrderAcceptAPIView.as_view(), name='order-food-accept'),
    path('ofitsiant/order/on-way/put/<int:id>/', OfitsiantOrderOnTheWayAPIView.as_view(), name='order-food-on-way'),
    path('ofitsiant/order/delivered/put/<int:id>/', OfitsiantOrderDeliverAPIView.as_view(), name='order-food-delivered'),
    path('ofitsiant/delivereds/<int:month>/<int:year>/', OfitsiantDeliveredAPIView.as_view(), name='delivered-get'),
    # user
    path('user/foods/get/', FoodListAPIView.as_view(), name='food-list'),
    path('user/foods/rate/<int:id>/<int:rate>/', RateFoodAPIView.as_view(), name='food-rate'),
    path('user/orders/post/', UserOrderCreateAPIView.as_view(), name='order-create'),
    path('user/orders/get/', UserOrdersAPIView.as_view(), name='order-get'),
    path('user/orders/delete/<int:id>/', UserOrderDeleteAPIView.as_view(), name='order-delete'),
]
