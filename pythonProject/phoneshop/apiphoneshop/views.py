from rest_framework import viewsets, status
from rest_framework import permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product, Variant, Brand, ListImg, User, Cart, CartItem
from .permission import IsAdminOrOwner
from .serializers import ProductSerializer, VariantSerializer, CreateProductSerializer, UserSerializer, CartSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return CreateProductSerializer
        return ProductSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [IsAdminOrOwner()]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    queryset = Cart.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Chỉ hiển thị giỏ hàng của người dùng hiện tại
        return Cart.objects.filter(User=self.request.user)

    def get_cart(self):
        # Lấy giỏ hàng của người dùng hiện tại, nếu chưa có thì tạo mới
        cart, created = Cart.objects.get_or_create(User=self.request.user)
        return cart

    @action(detail=False, methods=['post'], url_path='add-to-cart')
    def add_to_cart(self, request):
        # Thêm sản phẩm vào giỏ hàng
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity', 1)

        # Kiểm tra xem variant có tồn tại hay không
        try:
            variant = Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            return Response({'error': 'Biến thể sản phẩm không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart()
        # Kiểm tra nếu sản phẩm đã có trong giỏ hàng
        cart_item, created = CartItem.objects.get_or_create(Cart=cart, Variant=variant)

        if not created:
            # Nếu sản phẩm đã có, tăng số lượng
            cart_item.Quantity += int(quantity)
        else:
            cart_item.Quantity = int(quantity)
        cart_item.save()

        return Response({'success': 'Sản phẩm đã được thêm vào giỏ hàng.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='remove-from-cart')
    def remove_from_cart(self, request):
        # Xóa sản phẩm khỏi giỏ hàng
        variant_id = request.data.get('variant_id')

        # Kiểm tra xem variant có tồn tại hay không
        try:
            variant = Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            return Response({'error': 'Biến thể sản phẩm không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart()
        try:
            cart_item = CartItem.objects.get(Cart=cart, Variant=variant)
            cart_item.delete()
            return Response({'success': 'Sản phẩm đã được xóa khỏi giỏ hàng.'}, status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'error': 'Sản phẩm không có trong giỏ hàng.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'], url_path='update-quantity')
    def update_quantity(self, request):
        variant_id = request.data.get('variant_id')
        quantity = request.data.get('quantity')

        # Kiểm tra và ép kiểu quantity thành số nguyên
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({'error': 'Số lượng phải là một số nguyên hợp lệ.'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra số lượng có hợp lệ
        if quantity < 1:
            return Response({'error': 'Số lượng phải lớn hơn hoặc bằng 1.'}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra xem variant có tồn tại hay không
        try:
            variant = Variant.objects.get(id=variant_id)
        except Variant.DoesNotExist:
            return Response({'error': 'Biến thể sản phẩm không tồn tại.'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart()
        try:
            cart_item = CartItem.objects.get(Cart=cart, Variant=variant)
            cart_item.Quantity = quantity
            cart_item.save()
            return Response({'success': 'Số lượng sản phẩm đã được cập nhật.'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Sản phẩm không có trong giỏ hàng.'}, status=status.HTTP_404_NOT_FOUND)


class VariantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Variant.objects.all()
    serializer_class = VariantSerializer

    def get_permissions(self):
        return [permissions.AllowAny()]

    def get_queryset(self):
        # Trả về queryset chỉ chứa Variant có id phù hợp với tham số id trong URL
        variant_id = self.kwargs.get('pk')  # pk là tham số mặc định đại diện cho id trong URL
        return Variant.objects.filter(id=variant_id)

    def retrieve(self, request, *args, **kwargs):
        # Override phương thức retrieve để trả về kết quả theo id (pk)
        return super().retrieve(request, *args, **kwargs)
