from rest_framework import serializers
from .models import Product, Variant, Brand, ListImg


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
