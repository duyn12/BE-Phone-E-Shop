from rest_framework import serializers
from .models import Product, Variant, Brand, ListImg, User, CartItem, Cart, OrderDetail, Order


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'Name']


class ListImgSerializer(serializers.ModelSerializer):
    url_TitlePhoto = serializers.SerializerMethodField()

    class Meta:
        model = ListImg
        fields = ['id', 'url_TitlePhoto']

    def get_url_TitlePhoto(self, obj):
        return obj.TitlePhoto.url if obj.TitlePhoto else None


class VariantSerializer(serializers.ModelSerializer):
    img_url = serializers.SerializerMethodField()

    class Meta:
        model = Variant
        fields = [
            'id',
            'Product',
            'SKU',
            'Memory',
            'Color',
            'Quantity',
            'Price',
            'CompareAtPrice',
            'img_url',
        ]

    def get_img_url(self, obj):
        return obj.Img.url if obj.Img else None


class ProductSerializer(serializers.ModelSerializer):
    Brand = BrandSerializer(read_only=True)
    images = ListImgSerializer(many=True, read_only=True)
    variants = VariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'Name',
            'Brand',
            'Description',
            'TechnicalSpecifications',
            'images',
            'variants',
        ]


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'Name',
            'Brand',
            'Description',
            'TechnicalSpecifications',
        ]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'Phone_number', 'Address',
                  'Date_of_birth']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()

        return user


class CartItemSerializer(serializers.ModelSerializer):
    Variant = VariantSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'Variant', 'Quantity']

    def validate_Quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Số lượng phải lớn hơn hoặc bằng 1")
        return value


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'User', 'cart_items']
        read_only_fields = ['User']


class OrderDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDetail
        fields = ['id', 'Variant', 'Quantity', 'Price', 'Status']


class OrderSerializer(serializers.ModelSerializer):
    order_details = OrderDetailSerializer(many=True, read_only=True)
    short_link = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'User', 'Discount', 'Note', 'ShipAddress', 'ShipDate', 'Payment', 'order_details', 'short_link']

    def get_short_link(self, obj):
        return obj.short_link if hasattr(obj, 'short_link') else None


class PlaceOrderSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    discount_code = serializers.CharField(required=False, allow_blank=True)
    ship_address = serializers.CharField()
    payment = serializers.CharField()
