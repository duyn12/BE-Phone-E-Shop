from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, UserViewSet, CartViewSet, VariantViewSet, OrderViewSet, CommentViewSet

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('user', UserViewSet)
router.register('cart', CartViewSet)
router.register('variants', VariantViewSet)
router.register('order', OrderViewSet)
router.register('cmt', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
