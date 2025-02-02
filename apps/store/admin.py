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


class ProductsAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "type")


admin.site.register(Product, ProductsAdmin)
admin.site.register(Category)
admin.site.register(Attribute)
admin.site.register(AttributeOption)
admin.site.register(ProductAttribute)
admin.site.register(VideoPart)
admin.site.register(Sell)
admin.site.register(Claim)
