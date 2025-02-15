from django.contrib import admin
from store.models import (
    Attribute,
    AttributeOption,
    Category,
    Claim,
    Product,
    ProductAttribute,
    Sell,
    VideoPart,
)

# Register your models here.


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1


class VideoPartInline(admin.TabularInline):
    model = VideoPart
    extra = 1


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "type")
    inlines = [ProductAttributeInline, VideoPartInline]


admin.site.register(Product, ProductsAdmin)
admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(AttributeOption)
# admin.site.register(ProductAttribute)
# admin.site.register(VideoPart)
admin.site.register(Sell)
admin.site.register(Claim)
