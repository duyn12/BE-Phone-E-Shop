import json
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import User, Brand, Product, ListImg, Variant, Order, OrderDetail, Comment, Discount, Cart, CartItem


# Inline cho Variant và ListImg trong Product
class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1  # Số dòng trống khi thêm mới


class ListImgInline(admin.TabularInline):
    model = ListImg
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name', 'Brand', 'created_date', 'update_date')
    search_fields = ('Name', 'Brand__Name')
    list_filter = ('Brand', 'created_date')
    autocomplete_fields = ['Brand']
    inlines = [VariantInline, ListImgInline]  # Inline Variant và ListImg


# Inline CartItem vào Cart
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1  # Số dòng trống khi thêm mới


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'User', 'created_date', 'update_date')
    search_fields = ('User__username',)
    list_filter = ('created_date',)
    inlines = [CartItemInline]  # Inline CartItem vào Cart


# Inline OrderDetail vào Order
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 1  # Số dòng trống khi thêm mới


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Discount', 'ShipAddress', 'ShipDate', 'created_date')
    search_fields = ('User__username', 'ShipAddress', 'Discount__Code')
    list_filter = ('created_date',)
    autocomplete_fields = ['User', 'Discount']
    inlines = [OrderDetailInline]  # Inline OrderDetail vào Order


# User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'Date_of_birth', 'Phone_number', 'Address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email',
                       'Date_of_birth', 'Phone_number', 'Address', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'Phone_number')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')

    def get_fieldsets(self, request, obj=None):
        """Override get_fieldsets to use different fieldsets for change and add forms."""
        if not obj:
            return self.add_fieldsets
        return super(UserAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """Ensure required fields in add form."""
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        if not obj:
            # Set required fields for add form
            for field_name in ['first_name', 'last_name', 'email', 'Date_of_birth', 'Phone_number', 'Address']:
                if field_name in form.base_fields:
                    form.base_fields[field_name].required = True
        return form


# Brand Admin
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'Name', 'created_date', 'update_date')
    search_fields = ('Name',)
    list_filter = ('created_date',)


# Comment Admin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'User', 'Variant', 'Star', 'created_date')
    search_fields = ('User__username', 'Variant__SKU')
    list_filter = ('Star', 'created_date')
    autocomplete_fields = ['User', 'Variant']


# Discount Admin
@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('id', 'Code', 'DiscountPercent', 'DiscountMoney', 'StartDate', 'EndDate', 'created_date')
    search_fields = ('Code',)
    list_filter = ('StartDate', 'EndDate', 'created_date')


# CartItem Admin (nếu cần)
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'Cart', 'Variant', 'Quantity', 'created_date', 'update_date')
    search_fields = ('Cart__User__username', 'Variant__SKU')
    list_filter = ('created_date',)


# OrderDetail Admin
@admin.register(OrderDetail)
class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('id', 'Order', 'Variant', 'Quantity', 'Price', 'Status', 'created_date')
    search_fields = ('Order__id', 'Variant__SKU')
    list_filter = ('Status', 'created_date')
    autocomplete_fields = ['Order', 'Variant']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'Product', 'SKU', 'Memory', 'Color', 'Quantity', 'Price', 'created_date')
    search_fields = ('Product__Name', 'SKU', 'Color')
    list_filter = ('Product', 'Memory', 'Color', 'created_date')
    autocomplete_fields = ['Product']
