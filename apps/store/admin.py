from django.contrib import admin
from store.models import (
    Attribute,
    AttributeOption,
    Category,
    Product,
    ProductAttribute,
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
