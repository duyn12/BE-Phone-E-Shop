from datetime import timezone, datetime

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework import permissions, generics
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Product, Variant, Brand, ListImg, User, Cart, CartItem, Order, OrderDetail, Discount, Comment
from .momo_payment import create_momo_payment
from .permission import IsAdminOrOwner, IsOwnerOrReadOnly
from .serializers import ProductSerializer, VariantSerializer, CreateProductSerializer, UserSerializer, CartSerializer, \
    OrderSerializer, PlaceOrderSerializer, CommentSerializer


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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user_email = response.data.get('email')

        subject = "Welcome to Our Platform"
        message = (
            f"Dear {response.data.get('username')},\n\n"
            "Thank you for registering with us. We are excited to have you on board!\n\n"
            "Best regards,\nYour Platform Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        return response


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
        cart_item_id = request.data.get('cart_item_id')
        cart = self.get_cart()
        try:
            cart_item = CartItem.objects.get(Cart=cart, id=cart_item_id)
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


class OrderViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Order.objects.all()

    def get_permissions(self):
        if self.action == 'check_order':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        variant_id = serializer.validated_data['variant_id']
        quantity = serializer.validated_data['quantity']
        discount_code = serializer.validated_data.get('discount_code')
        ship_address = serializer.validated_data['ship_address']
        payment = serializer.validated_data['payment']

        # Fetch variant
        variant = get_object_or_404(Variant, id=variant_id)

        if variant.Quantity < quantity:
            return Response({"detail": "Not enough stock for this variant."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total price
        if variant.CompareAtPrice:
            price = variant.CompareAtPrice * quantity
        else:
            price = variant.Price * quantity

        # Fetch discount if provided
        discount = None
        if discount_code:
            discount = Discount.objects.filter(Code=discount_code, StartDate__lte=datetime.now(),
                                               EndDate__gte=datetime.now()).first()
            if not discount:
                return Response({"detail": "Invalid or expired discount code."}, status=status.HTTP_400_BAD_REQUEST)

            if discount.DiscountPercent:
                price -= price * (discount.DiscountPercent / 100)
            elif discount.DiscountMoney:
                price -= discount.DiscountMoney

        # Ensure price is not negative
        price = max(price, 0)

        # Create Order
        order = Order.objects.create(
            User=user,
            Discount=discount,
            ShipAddress=ship_address,
            ShipDate=request.data.get('ship_date', datetime.now()),
            Payment=payment
        )

        # Create OrderDetail
        order_detail = OrderDetail.objects.create(
            Order=order,
            Variant=variant,
            Quantity=quantity,
            Price=price,
            Status='Pending'
        )
        if payment == 'MoMo':
            momo_response = create_momo_payment(
                amount=(int)(price)
            )
            if isinstance(momo_response, dict):
                if momo_response.get('resultCode') == 0:
                    short_link = momo_response.get('payUrl')
                    order.short_link = short_link
                    order_detail.Status = "Done"
                    order_detail.save()

        # Decrease variant stock
        variant.Quantity -= quantity
        variant.save()

        # send mail to customer
        subject = "Order Confirmation"
        message = (
            f"Dear {user.username},\n\n"
            f"Thank you for your order!\n\n"
            f"Order Details:\n"
            f"- Order ID: {order.id}\n"
            f"- Product: {variant.Product.Name}\n"
            f"- Variant: {variant.SKU}\n"
            f"- Quantity: {quantity}\n"
            f"- Total Price: ${price:.2f}\n\n"
            f"Shipping to: {ship_address}\n"
            f"Payment Method: {payment}\n\n"
            f"Best regards,\nYour Store Team"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my-orders')
    def my_orders(self, request):
        user = request.user
        orders = Order.objects.filter(User=user).prefetch_related('order_details')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='check-order')
    def check_order(self, request):
        phone_number = request.data.get('phone_number')
        order_code = request.data.get('order_code')

        if not phone_number or not order_code:
            return Response({"detail": "Phone number and order code are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the order
        order = Order.objects.filter(User__Phone_number=phone_number, id=order_code).first()

        if not order:
            return Response({"detail": "Order not found or phone number does not match."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(User=self.request.user)

    def perform_update(self, serializer):
        if not self.get_object().User == self.request.user:
            raise PermissionDenied("You do not have permission to edit this comment.")
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.User == self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()
